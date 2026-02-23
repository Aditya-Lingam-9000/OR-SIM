"""
backend/llm/output_parser.py
Robust JSON extraction and validation from MedGemma raw output text.

MedGemma sometimes:
  - Wraps JSON in markdown code fences (```json ... ```)
  - Adds a preamble sentence before the JSON
  - Outputs slightly malformed JSON (trailing commas, single quotes)
  - Occasionally hallucinates extra keys

This parser handles all of the above with a cascade of strategies:
  1. Direct json.loads() on the full response
  2. Extract first {...} block and json.loads()
  3. Strip markdown code fences and retry
  4. Fix common LLM JSON errors (trailing commas, single→double quotes)
  5. Fuzzy machine name matching against the surgery's canonical names
  6. Return a safe empty-state fallback on complete failure
"""

from __future__ import annotations

import json
import re
from typing import Optional

from loguru import logger

from backend.data.surgeries import SurgeryType, MACHINES, get_machine_names
from backend.llm.schemas    import LLMOutput


def _build_alias_map(surgery: SurgeryType) -> dict[str, str]:
    """
    Build a lowercase alias → canonical name mapping for a surgery.
    Includes the canonical name itself as a key.

    Example:
      'bypass pump'               → 'Cardiopulmonary Bypass Machine'
      'cpb'                       → 'Cardiopulmonary Bypass Machine'
      'cardiopulmonary bypass ...' → 'Cardiopulmonary Bypass Machine'
      'or lights'                 → 'Surgical Lights'
    """
    alias_map: dict[str, str] = {}
    for machine in MACHINES[surgery].values():
        canonical = machine["name"]
        alias_map[canonical.lower()] = canonical
        for alias in machine.get("aliases", []):
            alias_map[alias.lower()] = canonical
    return alias_map


# ── JSON extraction strategies ────────────────────────────────────────────────

def _strip_code_fence(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers."""
    text = re.sub(r"```(?:json)?\s*", "", text)
    text = text.replace("```", "")
    return text.strip()


def _fix_trailing_commas(text: str) -> str:
    """Remove trailing commas before ] or } (invalid JSON but common LLM output)."""
    return re.sub(r",\s*([\]}])", r"\1", text)


def _fix_single_quotes(text: str) -> str:
    """Replace single-quoted strings with double-quoted (heuristic, not perfect)."""
    return re.sub(r"(?<![\\])'", '"', text)


def _extract_first_json_object(text: str) -> Optional[str]:
    """Extract the first {...} block from a string, handling nested braces."""
    depth  = 0
    start  = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                return text[start : i + 1]
    return None


def _try_parse(text: str) -> Optional[dict]:
    """Attempt json.loads with progressive repairs."""
    candidates = [
        text,
        _strip_code_fence(text),
        _fix_trailing_commas(text),
        _fix_trailing_commas(_strip_code_fence(text)),
    ]
    extracted = _extract_first_json_object(text)
    if extracted:
        candidates += [
            extracted,
            _fix_trailing_commas(extracted),
        ]

    for candidate in candidates:
        try:
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
    return None


# ── machine name fuzzy matcher ────────────────────────────────────────────────

def _fuzzy_match_machine(
    name: str,
    canonical_names: list[str],
    alias_map: dict[str, str],
) -> Optional[str]:
    """
    Try to match an LLM-output machine name to a canonical name.
    Resolution order:
      1. Exact alias/canonical name match (case-insensitive)
      2. Alias map substring — alias IS a substring of the input
      3. Canonical name substring — both directions
    Returns the canonical name if found, else None.
    """
    name_lower = name.lower().strip()

    # 1. Exact alias/canonical lookup
    if name_lower in alias_map:
        return alias_map[name_lower]

    # 2. alias map key is a substring of the input (e.g. input='bypass pump activated')
    for alias_key, canonical in alias_map.items():
        if alias_key in name_lower:
            return canonical

    # 3. Canonical name substring fallback (both directions)
    for c in canonical_names:
        if name_lower in c.lower() or c.lower() in name_lower:
            return c

    return None


def _normalise_machine_names(
    machine_list: list[str],
    canonical_names: list[str],
    alias_map: dict[str, str],
    label: str,
) -> list[str]:
    """Map LLM-output machine names to canonical names, dropping unknowns."""
    result = []
    for name in machine_list:
        matched = _fuzzy_match_machine(name, canonical_names, alias_map)
        if matched:
            if matched not in result:
                result.append(matched)
        else:
            logger.warning(f"  OutputParser: unknown machine in {label}: {name!r}")
    return result


# ── main entry point ──────────────────────────────────────────────────────────

def parse_llm_output(
    raw_text: str,
    surgery: SurgeryType,
) -> LLMOutput:
    """
    Parse MedGemma's raw text response into a validated LLMOutput.

    Parameters
    ----------
    raw_text : str          The raw string returned by MedGemma
    surgery  : SurgeryType  Used for fuzzy machine name normalisation

    Returns
    -------
    LLMOutput  (always — falls back to empty lists on total failure)
    """
    canonical_names = get_machine_names(surgery)
    alias_map       = _build_alias_map(surgery)

    parsed = _try_parse(raw_text)

    if parsed is None:
        logger.warning(f"OutputParser: could not parse JSON from:\n{raw_text[:300]!r}")
        return LLMOutput(reasoning="Parse failed — no state change applied.")

    # Extract machine_states with safe fallback
    machine_states_raw = parsed.get("machine_states", {})
    if not isinstance(machine_states_raw, dict):
        machine_states_raw = {}

    turn_off_raw = machine_states_raw.get("0", [])
    turn_on_raw  = machine_states_raw.get("1", [])

    if not isinstance(turn_off_raw, list):
        turn_off_raw = []
    if not isinstance(turn_on_raw, list):
        turn_on_raw = []

    # Normalise machine names (canonical + alias aware)
    turn_off = _normalise_machine_names(turn_off_raw, canonical_names, alias_map, label="turn_off")
    turn_on  = _normalise_machine_names(turn_on_raw,  canonical_names, alias_map, label="turn_on")

    reasoning = str(parsed.get("reasoning", "")).strip()

    result = LLMOutput(
        reasoning      = reasoning,
        machine_states = {"0": turn_off, "1": turn_on},
    )

    logger.debug(
        f"OutputParser: turn_on={turn_on} | turn_off={turn_off} | reasoning={reasoning!r:.80}"
    )
    return result


# ── CLI self-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from backend.data.surgeries import SurgeryType

    SURGERY = SurgeryType.HEART_TRANSPLANT

    test_cases = [
        # (description, raw_text)
        (
            "Clean JSON response",
            '{"reasoning": "Surgeon said to activate monitoring.", '
            '"machine_states": {"0": [], "1": ["Patient Monitor"]}}',
        ),
        (
            "JSON wrapped in code fence",
            '```json\n{"reasoning": "Starting bypass.", "machine_states": {"0": ["Ventilator"], "1": ["Cardiopulmonary Bypass Machine"]}}\n```',
        ),
        (
            "JSON with preamble text",
            'Sure! Here is the output:\n{"reasoning": "Lights needed.", "machine_states": {"0": [], "1": ["Surgical Lights"]}}',
        ),
        (
            "Trailing comma (malformed)",
            '{"reasoning": "Defib on.", "machine_states": {"0": [], "1": ["Defibrillator",]}}',
        ),
        (
            "Fuzzy machine name (alias match)",
            '{"reasoning": "Bypass started.", "machine_states": {"0": ["vent"], "1": ["bypass machine"]}}',
        ),
        (
            "Unknown machine name",
            '{"reasoning": "Unknown device.", "machine_states": {"0": [], "1": ["Laser Scalpel 3000"]}}',
        ),
        (
            "Completely invalid",
            "I cannot determine which machines to control.",
        ),
    ]

    print(f"\n{'='*65}")
    print(f"  OutputParser tests — {SURGERY}")
    print(f"{'='*65}")

    for desc, raw in test_cases:
        result = parse_llm_output(raw, SURGERY)
        print(f"\n[{desc}]")
        print(f"  Turn ON  : {result.machine_states['1']}")
        print(f"  Turn OFF : {result.machine_states['0']}")
        print(f"  Reasoning: {result.reasoning[:80]!r}")
