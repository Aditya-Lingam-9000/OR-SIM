"""
backend/data/state_manager.py
StateManager — tracks machine on/off states for the active surgery and
writes atomically to output/machine_states.json on every update.

Key design decisions:
  • All machines start in the OFF (0) state when a session begins.
  • Atomic write: write to a .tmp file then os.replace() to ensure the
    frontend never reads a half-written JSON.
  • Thread-safe: a threading.Lock guards all state mutations.
  • Callbacks: optional list of callables invoked after every state update,
    used by the WebSocket broadcaster (Phase 5) to push diffs to clients.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from loguru import logger

from backend.data.surgeries import MACHINES, SurgeryType, get_machine_names
from backend.data.models    import MachineEntry, ORStateSnapshot, StateUpdateRequest

# ── output path ───────────────────────────────────────────────────────────────
_OUTPUT_DIR  = Path(__file__).parent.parent.parent / "output"
_STATE_FILE  = _OUTPUT_DIR / "machine_states.json"
_STATE_TMP   = _OUTPUT_DIR / "machine_states.json.tmp"


class StateManager:
    """
    Manages the live on/off state of all machines for a chosen surgery.

    Usage
    -----
    sm = StateManager(SurgeryType.HEART_TRANSPLANT)
    sm.apply_update(StateUpdateRequest(
        turn_on  = ["Patient Monitor", "Ventilator"],
        turn_off = [],
        transcription = "turn on the patient monitor and ventilator",
        reasoning     = "Doctor said to activate monitoring and ventilation",
    ))
    # → output/machine_states.json updated atomically
    """

    def __init__(
        self,
        surgery: SurgeryType,
        on_update_callbacks: Optional[list[Callable[[ORStateSnapshot], None]]] = None,
    ):
        self.surgery   = surgery
        self._lock     = threading.Lock()
        self._callbacks: list[Callable[[ORStateSnapshot], None]] = on_update_callbacks or []

        # Build internal state: {canonical_name: MachineEntry}
        self._machines: dict[str, MachineEntry] = {}
        for entry in MACHINES[surgery].values():
            self._machines[entry["name"]] = MachineEntry(
                name        = entry["name"],
                description = entry["description"],
                is_on       = False,
            )

        # Ensure output dir exists
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # Write initial "all off" state
        self._last_transcription = ""
        self._last_reasoning     = ""
        self._write_json()

        logger.info(
            f"StateManager initialised — surgery={surgery}, "
            f"machines={len(self._machines)}, output={_STATE_FILE}"
        )

    # ── public API ────────────────────────────────────────────────────────────

    def apply_update(self, req: StateUpdateRequest) -> ORStateSnapshot:
        """
        Apply a state update request: turn specified machines on/off.

        Unknown machine names are logged as warnings and skipped.
        Returns the new ORStateSnapshot after applying changes.
        """
        with self._lock:
            changed = False

            for name in req.turn_on:
                matched = self._resolve_name(name)
                if matched:
                    if not self._machines[matched].is_on:
                        self._machines[matched].is_on = True
                        logger.info(f"  ▶ ON  : {matched}")
                        changed = True
                else:
                    logger.warning(f"  ⚠ Unknown machine (turn_on): {name!r}")

            for name in req.turn_off:
                matched = self._resolve_name(name)
                if matched:
                    if self._machines[matched].is_on:
                        self._machines[matched].is_on = False
                        logger.info(f"  ■ OFF : {matched}")
                        changed = True
                else:
                    logger.warning(f"  ⚠ Unknown machine (turn_off): {name!r}")

            self._last_transcription = req.transcription
            self._last_reasoning     = req.reasoning

            snapshot = self._build_snapshot()
            self._write_json(snapshot)

        # Fire callbacks outside the lock
        for cb in self._callbacks:
            try:
                cb(snapshot)
            except Exception as exc:
                logger.error(f"StateManager callback error: {exc}")

        return snapshot

    def get_snapshot(self) -> ORStateSnapshot:
        """Return current state without modifying anything."""
        with self._lock:
            return self._build_snapshot()

    def reset(self) -> ORStateSnapshot:
        """Turn all machines OFF and write initial state."""
        with self._lock:
            for m in self._machines.values():
                m.is_on = False
            self._last_transcription = ""
            self._last_reasoning     = ""
            snapshot = self._build_snapshot()
            self._write_json(snapshot)
        logger.info("StateManager: all machines reset to OFF")
        return snapshot

    def register_callback(self, cb: Callable[[ORStateSnapshot], None]) -> None:
        """Register a callback invoked after every state change."""
        self._callbacks.append(cb)

    # ── internal ──────────────────────────────────────────────────────────────

    def _resolve_name(self, name: str) -> Optional[str]:
        """
        Find the canonical machine name for a given input string.
        Tries exact match first, then case-insensitive, then partial match.
        Returns None if no match found.
        """
        # 1. Exact match
        if name in self._machines:
            return name

        # 2. Case-insensitive exact
        name_lower = name.lower().strip()
        for canonical in self._machines:
            if canonical.lower() == name_lower:
                return canonical

        # 3. Partial match (canonical name starts with or contains the input)
        for canonical in self._machines:
            if name_lower in canonical.lower():
                return canonical

        return None

    def _build_snapshot(self) -> ORStateSnapshot:
        """Build an ORStateSnapshot from current internal state (call under lock)."""
        off_machines = [name for name, m in self._machines.items() if not m.is_on]
        on_machines  = [name for name, m in self._machines.items() if m.is_on]

        return ORStateSnapshot(
            surgery        = str(self.surgery),
            timestamp      = datetime.now(timezone.utc).isoformat(),
            transcription  = self._last_transcription,
            reasoning      = self._last_reasoning,
            machine_states = {
                "0": off_machines,
                "1": on_machines,
            },
        )

    def _write_json(self, snapshot: Optional[ORStateSnapshot] = None) -> None:
        """
        Atomically write current state to output/machine_states.json.
        Uses write-to-tmp + os.replace() to prevent partial reads.
        """
        if snapshot is None:
            snapshot = self._build_snapshot()

        payload = json.dumps(snapshot.to_json_dict(), indent=2, ensure_ascii=False)

        try:
            _STATE_TMP.write_text(payload, encoding="utf-8")
            os.replace(_STATE_TMP, _STATE_FILE)
        except Exception as exc:
            logger.error(f"Failed to write state JSON: {exc}")


# ── CLI self-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import time

    print("\n── HEART TRANSPLANTATION state demo ──────────────────────────\n")
    sm = StateManager(SurgeryType.HEART_TRANSPLANT)

    steps = [
        StateUpdateRequest(
            turn_on       = ["Patient Monitor", "Anesthesia Machine"],
            turn_off      = [],
            transcription = "turn on the patient monitor and anesthesia machine",
            reasoning     = "Initial setup — monitoring and anesthesia first",
        ),
        StateUpdateRequest(
            turn_on       = ["Ventilator", "Surgical Lights"],
            turn_off      = [],
            transcription = "activate the ventilator and turn on the lights",
            reasoning     = "Ventilation and lighting needed before incision",
        ),
        StateUpdateRequest(
            turn_on       = ["Cardiopulmonary Bypass Machine", "Perfusion Pump"],
            turn_off      = ["Ventilator"],
            transcription = "start the bypass machine and stop the ventilator",
            reasoning     = "CPB taking over — lungs bypassed",
        ),
    ]

    for i, req in enumerate(steps, 1):
        print(f"\n[Step {i}] Transcription: \"{req.transcription}\"")
        snap = sm.apply_update(req)
        print(f"  ON  : {snap.machine_states['1']}")
        print(f"  OFF : {snap.machine_states['0']}")
        time.sleep(0.2)

    print(f"\nJSON written to: {_STATE_FILE}")
    print("\nFinal JSON preview:")
    print(_STATE_FILE.read_text(encoding="utf-8"))
