"""
tests/phase2/test_data.py
Phase 2 tests — Surgery & Machines Data Layer.

Run:
    cd d:\\OR-SIM
    venv\\Scripts\\python.exe -m pytest tests/phase2/test_data.py -v

Covers:
    1. Surgery type enum values
    2. Machine dictionary completeness (all 3 surgeries, 12 machines each)
    3. Machine name uniqueness per surgery
    4. Aliases present for all machines
    5. Pydantic model construction and serialisation
    6. StateManager initialisation — all machines start OFF
    7. StateManager apply_update — correct ON/OFF transitions
    8. StateManager reset — returns all OFF
    9. StateManager fuzzy name resolution (partial / case-insensitive)
    10. Atomic JSON file written on every update
    11. JSON schema validation (keys "0" and "1" present, values are lists)
    12. Thread-safety — concurrent updates don't corrupt state
"""

import json
import sys
import threading
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data.surgeries     import SurgeryType, MACHINES, get_machine_names, get_machines_formatted
from backend.data.models        import ORStateSnapshot, StateUpdateRequest, MachineEntry
from backend.data.state_manager import StateManager, _STATE_FILE


# ── Surgery enum ──────────────────────────────────────────────────────────────

class TestSurgeryType:

    def test_three_surgery_types(self):
        assert len(SurgeryType) == 3

    def test_heart_value(self):
        assert str(SurgeryType.HEART_TRANSPLANT) == "Heart Transplantation"

    def test_liver_value(self):
        assert str(SurgeryType.LIVER_RESECTION) == "Liver Resection"

    def test_kidney_value(self):
        assert str(SurgeryType.KIDNEY_PCNL) == "Kidney PCNL"


# ── Machine dictionaries ──────────────────────────────────────────────────────

class TestMachineDictionaries:

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_twelve_machines_per_surgery(self, surgery):
        assert len(MACHINES[surgery]) == 12, (
            f"{surgery} has {len(MACHINES[surgery])} machines, expected 12"
        )

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_consecutive_indices(self, surgery):
        keys = sorted(MACHINES[surgery].keys())
        assert keys == list(range(12)), f"{surgery}: indices not 0-11"

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_all_machines_have_required_fields(self, surgery):
        for idx, entry in MACHINES[surgery].items():
            assert "name"        in entry, f"{surgery}[{idx}] missing 'name'"
            assert "description" in entry, f"{surgery}[{idx}] missing 'description'"
            assert "aliases"     in entry, f"{surgery}[{idx}] missing 'aliases'"
            assert isinstance(entry["name"],        str),  f"{surgery}[{idx}] name not str"
            assert isinstance(entry["description"], str),  f"{surgery}[{idx}] description not str"
            assert isinstance(entry["aliases"],     list), f"{surgery}[{idx}] aliases not list"

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_unique_machine_names(self, surgery):
        names = [entry["name"] for entry in MACHINES[surgery].values()]
        assert len(names) == len(set(names)), f"{surgery} has duplicate machine names: {names}"

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_non_empty_names_and_descriptions(self, surgery):
        for idx, entry in MACHINES[surgery].items():
            assert entry["name"].strip(),        f"{surgery}[{idx}] name is empty"
            assert entry["description"].strip(), f"{surgery}[{idx}] description is empty"

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_all_machines_have_at_least_one_alias(self, surgery):
        for idx, entry in MACHINES[surgery].items():
            assert len(entry["aliases"]) >= 1, (
                f"{surgery}[{idx}] '{entry['name']}' has no aliases"
            )

    def test_patient_monitor_in_all_surgeries(self):
        """Patient Monitor is present in every surgery."""
        for surgery in SurgeryType:
            names = get_machine_names(surgery)
            assert "Patient Monitor" in names, f"{surgery} missing Patient Monitor"

    def test_surgical_lights_in_all_surgeries(self):
        for surgery in SurgeryType:
            names = get_machine_names(surgery)
            assert "Surgical Lights" in names, f"{surgery} missing Surgical Lights"

    def test_get_machines_formatted_output(self):
        text = get_machines_formatted(SurgeryType.HEART_TRANSPLANT)
        assert "Patient Monitor" in text
        assert "Cardiopulmonary Bypass Machine" in text
        assert "Defibrillator" in text
        # Should have 12 lines
        lines = [l for l in text.splitlines() if l.strip()]
        assert len(lines) == 12

    def test_get_machine_names_returns_list(self):
        names = get_machine_names(SurgeryType.LIVER_RESECTION)
        assert isinstance(names, list)
        assert len(names) == 12
        assert all(isinstance(n, str) for n in names)


# ── Pydantic models ───────────────────────────────────────────────────────────

class TestModels:

    def test_or_state_snapshot_defaults(self):
        snap = ORStateSnapshot(surgery="Heart Transplantation")
        assert snap.surgery == "Heart Transplantation"
        assert snap.machine_states == {"0": [], "1": []}
        assert snap.transcription == ""
        assert snap.timestamp     != ""

    def test_or_state_snapshot_serialises(self):
        snap = ORStateSnapshot(
            surgery        = "Liver Resection",
            transcription  = "turn on the lights",
            machine_states = {"0": ["Ventilator"], "1": ["Patient Monitor", "Surgical Lights"]},
        )
        d = snap.to_json_dict()
        assert d["surgery"]        == "Liver Resection"
        assert "Patient Monitor"   in d["machine_states"]["1"]
        assert "Ventilator"        in d["machine_states"]["0"]

    def test_state_update_request_defaults(self):
        req = StateUpdateRequest()
        assert req.turn_on  == []
        assert req.turn_off == []

    def test_state_update_request_fields(self):
        req = StateUpdateRequest(
            turn_on  = ["Patient Monitor"],
            turn_off = ["Ventilator"],
            transcription = "test",
            reasoning     = "test reason",
        )
        assert "Patient Monitor" in req.turn_on
        assert "Ventilator"      in req.turn_off

    def test_machine_entry_default_off(self):
        m = MachineEntry(name="Ventilator", description="breathing machine")
        assert m.is_on is False


# ── StateManager ──────────────────────────────────────────────────────────────

@pytest.fixture
def sm_heart():
    """Fresh StateManager for each test."""
    return StateManager(SurgeryType.HEART_TRANSPLANT)


@pytest.fixture
def sm_kidney():
    return StateManager(SurgeryType.KIDNEY_PCNL)


class TestStateManagerInit:

    def test_all_machines_start_off(self, sm_heart):
        snap = sm_heart.get_snapshot()
        assert snap.machine_states["1"] == [], "No machine should be ON at start"
        assert len(snap.machine_states["0"]) == 12

    def test_surgery_name_in_snapshot(self, sm_heart):
        snap = sm_heart.get_snapshot()
        assert snap.surgery == "Heart Transplantation"

    def test_json_file_created_on_init(self, sm_heart):
        assert _STATE_FILE.exists(), "machine_states.json should be created on init"

    def test_json_file_valid_on_init(self, sm_heart):
        data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        assert "machine_states" in data
        assert "0" in data["machine_states"]
        assert "1" in data["machine_states"]
        assert isinstance(data["machine_states"]["0"], list)
        assert isinstance(data["machine_states"]["1"], list)


class TestStateManagerUpdates:

    def test_turn_on_single_machine(self, sm_heart):
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["Patient Monitor"]))
        assert "Patient Monitor" in snap.machine_states["1"]
        assert "Patient Monitor" not in snap.machine_states["0"]

    def test_turn_off_machine(self, sm_heart):
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Ventilator"]))
        snap = sm_heart.apply_update(StateUpdateRequest(turn_off=["Ventilator"]))
        assert "Ventilator" not in snap.machine_states["1"]
        assert "Ventilator" in snap.machine_states["0"]

    def test_simultaneous_on_and_off(self, sm_heart):
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Ventilator"]))
        snap = sm_heart.apply_update(StateUpdateRequest(
            turn_on  = ["Patient Monitor", "Cardiopulmonary Bypass Machine"],
            turn_off = ["Ventilator"],
        ))
        assert "Patient Monitor"                in snap.machine_states["1"]
        assert "Cardiopulmonary Bypass Machine" in snap.machine_states["1"]
        assert "Ventilator"                     in snap.machine_states["0"]

    def test_transcription_and_reasoning_stored(self, sm_heart):
        snap = sm_heart.apply_update(StateUpdateRequest(
            turn_on       = ["Defibrillator"],
            transcription = "turn on the defib",
            reasoning     = "defibrillator needed for cardioversion",
        ))
        assert snap.transcription == "turn on the defib"
        assert snap.reasoning     == "defibrillator needed for cardioversion"

    def test_total_machines_constant(self, sm_heart):
        """ON + OFF count must always equal total machine count."""
        snap1 = sm_heart.apply_update(StateUpdateRequest(
            turn_on=["Patient Monitor", "Ventilator", "Surgical Lights"]
        ))
        total = len(snap1.machine_states["0"]) + len(snap1.machine_states["1"])
        assert total == 12

    def test_idempotent_turn_on(self, sm_heart):
        """Turning on an already-ON machine doesn't duplicate it."""
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Electrocautery Unit"]))
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["Electrocautery Unit"]))
        assert snap.machine_states["1"].count("Electrocautery Unit") == 1

    def test_unknown_machine_ignored(self, sm_heart):
        """Unknown machine name should be ignored, not crash."""
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["Laser Cannon"]))
        assert "Laser Cannon" not in snap.machine_states["1"]

    def test_reset_all_off(self, sm_heart):
        sm_heart.apply_update(StateUpdateRequest(
            turn_on=["Patient Monitor", "Ventilator", "Cardiopulmonary Bypass Machine"]
        ))
        snap = sm_heart.reset()
        assert snap.machine_states["1"] == []
        assert len(snap.machine_states["0"]) == 12


class TestStateManagerFuzzyResolution:

    def test_case_insensitive_match(self, sm_heart):
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["patient monitor"]))
        assert "Patient Monitor" in snap.machine_states["1"]

    def test_partial_name_match(self, sm_heart):
        """'bypass' should match 'Cardiopulmonary Bypass Machine'."""
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["bypass"]))
        assert "Cardiopulmonary Bypass Machine" in snap.machine_states["1"]

    def test_partial_match_kidney(self, sm_kidney):
        """'c-arm' should match 'Fluoroscopy C-Arm'."""
        snap = sm_kidney.apply_update(StateUpdateRequest(turn_on=["c-arm"]))
        assert "Fluoroscopy C-Arm" in snap.machine_states["1"]


class TestStateManagerJSON:

    def test_json_updates_on_every_apply(self, sm_heart):
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Warming Blanket"]))
        data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        assert "Warming Blanket" in data["machine_states"]["1"]

    def test_json_schema_always_valid(self, sm_heart):
        for name in ["Patient Monitor", "Ventilator", "Defibrillator"]:
            sm_heart.apply_update(StateUpdateRequest(turn_on=[name]))
        data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        assert set(data["machine_states"].keys()) == {"0", "1"}
        assert isinstance(data["machine_states"]["0"], list)
        assert isinstance(data["machine_states"]["1"], list)
        total = len(data["machine_states"]["0"]) + len(data["machine_states"]["1"])
        assert total == 12

    def test_json_has_timestamp(self, sm_heart):
        snap = sm_heart.apply_update(StateUpdateRequest(turn_on=["Blood Warmer"]))
        data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        assert "timestamp" in data
        assert len(data["timestamp"]) > 0


class TestStateManagerThreadSafety:

    def test_concurrent_updates_no_corruption(self, sm_heart):
        """Ten threads simultaneously turning different machines on should not crash
        and the final machine count must still be 12."""
        errors = []
        names  = get_machine_names(SurgeryType.HEART_TRANSPLANT)

        def worker(machine_name: str):
            try:
                sm_heart.apply_update(StateUpdateRequest(turn_on=[machine_name]))
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=worker, args=(n,)) for n in names]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == [], f"Thread errors: {errors}"
        snap = sm_heart.get_snapshot()
        total = len(snap.machine_states["0"]) + len(snap.machine_states["1"])
        assert total == 12


class TestStateManagerCallback:

    def test_callback_fired_on_update(self, sm_heart):
        received = []
        sm_heart.register_callback(lambda snap: received.append(snap))
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Suction Device"]))
        assert len(received) == 1
        assert isinstance(received[0], ORStateSnapshot)

    def test_callback_receives_correct_state(self, sm_heart):
        received = []
        sm_heart.register_callback(lambda snap: received.append(snap))
        sm_heart.apply_update(StateUpdateRequest(turn_on=["Perfusion Pump"]))
        assert "Perfusion Pump" in received[0].machine_states["1"]
