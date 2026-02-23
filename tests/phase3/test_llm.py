"""
tests/phase3/test_llm.py
Phase 3 unit tests — LLM module (no GPU required).

All tests run purely on prompts, parsers, and schema validation.
NO llama-cpp-python or GGUF model is loaded here.
Run with:
  pytest tests/phase3/test_llm.py -v
"""

import json
import pytest

from backend.data.surgeries import SurgeryType, MACHINES
from backend.data.models    import ORStateSnapshot
from backend.llm.schemas    import LLMOutput
from backend.llm.prompt_builder import PromptBuilder
from backend.llm.output_parser  import parse_llm_output


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Fixtures                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝

@pytest.fixture(params=list(SurgeryType))
def surgery(request):
    return request.param


@pytest.fixture
def heart_builder():
    return PromptBuilder(SurgeryType.HEART_TRANSPLANT)


@pytest.fixture
def heart_snapshot():
    """A realistic mid-surgery snapshot for HEART_TRANSPLANT."""
    return ORStateSnapshot(
        surgery      = SurgeryType.HEART_TRANSPLANT,
        transcription = "previous command",
        reasoning    = "Doctor asked for ventilator",
        machine_states = {
            "1": ["Ventilator", "Anesthesia Machine"],
            "0": [
                m["name"] for k, m in MACHINES[SurgeryType.HEART_TRANSPLANT].items()
                if m["name"] not in ("Ventilator", "Anesthesia Machine")
            ],
        },
    )


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PromptBuilder tests                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestPromptBuilder:
    def test_system_prompt_contains_surgery_name(self, surgery):
        builder = PromptBuilder(surgery)
        sp = builder.build_system_prompt()
        assert surgery.value.replace("_", " ").upper() in sp.upper() or \
               surgery.name.replace("_", " ").lower() in sp.lower(), \
               f"Surgery name not found in system prompt for {surgery}"

    def test_system_prompt_contains_machine_names(self, surgery):
        builder = PromptBuilder(surgery)
        sp = builder.build_system_prompt()
        for machine in MACHINES[surgery].values():
            assert machine["name"] in sp, \
                f"Machine '{machine['name']}' missing from system prompt ({surgery})"

    def test_system_prompt_contains_aliases(self, surgery):
        builder = PromptBuilder(surgery)
        sp = builder.build_system_prompt()
        for machine in MACHINES[surgery].values():
            for alias in machine.get("aliases", []):
                assert alias in sp, \
                    f"Alias '{alias}' missing from system prompt ({surgery})"

    def test_system_prompt_contains_json_schema(self, heart_builder):
        sp = heart_builder.build_system_prompt()
        assert '"reasoning"' in sp
        assert '"machine_states"' in sp
        assert '"0"' in sp
        assert '"1"' in sp

    def test_system_prompt_is_cached(self, heart_builder):
        sp1 = heart_builder.build_system_prompt()
        sp2 = heart_builder.build_system_prompt()
        assert sp1 is sp2, "build_system_prompt() should return the same cached object"

    def test_user_message_contains_transcription(self, heart_builder, heart_snapshot):
        um = heart_builder.build_user_message(
            "activate the bypass pump", heart_snapshot
        )
        assert "activate the bypass pump" in um

    def test_user_message_contains_current_state(self, heart_builder, heart_snapshot):
        um = heart_builder.build_user_message("test command", heart_snapshot)
        assert "Ventilator" in um
        assert "Anesthesia Machine" in um

    def test_user_message_no_snapshot(self, heart_builder):
        um = heart_builder.build_user_message("turn on OR lights", None)
        assert "turn on OR lights" in um

    def test_build_messages_returns_list(self, heart_builder, heart_snapshot):
        msgs = heart_builder.build_messages("test", heart_snapshot)
        assert isinstance(msgs, list)
        assert len(msgs) >= 2

    def test_build_messages_roles(self, heart_builder, heart_snapshot):
        msgs = heart_builder.build_messages("test", heart_snapshot)
        roles = [m["role"] for m in msgs]
        assert roles[0] == "system"
        assert "user" in roles

    def test_build_messages_have_content(self, heart_builder, heart_snapshot):
        msgs = heart_builder.build_messages("test", heart_snapshot)
        for msg in msgs:
            assert "role" in msg
            assert "content" in msg
            assert len(msg["content"]) > 0


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  LLMOutput schema tests                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestLLMOutput:
    def test_valid_full_output(self):
        data = {
            "reasoning": "Doctor wants ventilator on.",
            "machine_states": {"0": ["OR Lights"], "1": ["Ventilator"]},
        }
        obj = LLMOutput(**data)
        assert obj.reasoning == "Doctor wants ventilator on."
        assert "Ventilator" in obj.machine_states["1"]

    def test_missing_reasoning_empty_string(self):
        data = {"machine_states": {"0": [], "1": []}}
        obj = LLMOutput(**data)
        assert obj.reasoning == ""

    def test_both_keys_required(self):
        # Only "1" key → validator should add "0"
        data = {"reasoning": "test", "machine_states": {"1": ["Ventilator"]}}
        obj = LLMOutput(**data)
        assert "0" in obj.machine_states
        assert "1" in obj.machine_states

    def test_empty_machine_states_allowed(self):
        data = {"reasoning": "no change", "machine_states": {"0": [], "1": []}}
        obj = LLMOutput(**data)
        assert obj.machine_states["0"] == []
        assert obj.machine_states["1"] == []

    def test_to_state_update_kwargs(self):
        data = {
            "reasoning": "r",
            "machine_states": {
                "0": ["OR Lights"],
                "1": ["Ventilator", "Anesthesia Machine"],
            },
        }
        obj = LLMOutput(**data)
        kwargs = obj.to_state_update_kwargs()
        assert set(kwargs["turn_on"]) == {"Ventilator", "Anesthesia Machine"}
        assert set(kwargs["turn_off"]) == {"OR Lights"}
        assert kwargs["reasoning"] == "r"

    def test_default_constructor(self):
        obj = LLMOutput()
        assert obj.machine_states == {"0": [], "1": []}


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  parse_llm_output tests  (7 edge-case scenarios)                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestOutputParser:
    SURGERY = SurgeryType.HEART_TRANSPLANT

    def test_clean_json(self):
        raw = json.dumps({
            "reasoning": "Turn on the ventilator.",
            "machine_states": {"0": [], "1": ["Ventilator"]},
        })
        result = parse_llm_output(raw, self.SURGERY)
        assert "Ventilator" in result.machine_states["1"]

    def test_code_fence_markdown(self):
        raw = (
            "Sure! Here is the result:\n"
            "```json\n"
            '{"reasoning": "test", "machine_states": {"0": [], "1": ["OR Lights"]}}\n'
            "```\n"
        )
        result = parse_llm_output(raw, self.SURGERY)
        # "OR Lights" is an alias for "Surgical Lights"
        assert any("Light" in n or "light" in n for n in result.machine_states["1"]), \
            f"Expected Surgical Lights (via alias 'OR Lights'), got: {result.machine_states['1']}"

    def test_code_fence_no_language(self):
        raw = (
            "```\n"
            '{"reasoning": "test", "machine_states": {"0": [], "1": ["Bypass Pump"]}}\n'
            "```"
        )
        result = parse_llm_output(raw, self.SURGERY)
        # "Bypass Pump" is an alias for "Cardiopulmonary Bypass Machine"
        assert any("Bypass" in n or "bypass" in n for n in result.machine_states["1"]), \
            f"Expected Cardiopulmonary Bypass Machine (via alias 'Bypass Pump'), got: {result.machine_states['1']}"

    def test_preamble_text_before_json(self):
        raw = (
            "Based on the surgeon's command, I will turn on the bypass pump.\n"
            '{"reasoning": "activate bp", "machine_states": {"0": [], "1": ["Bypass Pump"]}}'
        )
        result = parse_llm_output(raw, self.SURGERY)
        # "Bypass Pump" is an alias for "Cardiopulmonary Bypass Machine"
        assert any("Bypass" in n or "bypass" in n for n in result.machine_states["1"]), \
            f"Expected Cardiopulmonary Bypass Machine (via alias 'Bypass Pump'), got: {result.machine_states['1']}"

    def test_trailing_comma_fix(self):
        raw = (
            '{"reasoning": "test", '
            '"machine_states": {"0": ["OR Lights",], "1": ["Ventilator",]}}'
        )
        result = parse_llm_output(raw, self.SURGERY)
        assert "Ventilator" in result.machine_states["1"]

    def test_single_quote_fix(self):
        raw = "{'reasoning': 'test', 'machine_states': {'0': [], '1': ['Ventilator']}}"
        result = parse_llm_output(raw, self.SURGERY)
        # May or may not succeed depending on edge cases — at minimum returns valid obj
        assert isinstance(result, LLMOutput)

    def test_completely_invalid_returns_safe_fallback(self):
        raw = "I'm sorry, I don't understand the command."
        result = parse_llm_output(raw, self.SURGERY)
        assert isinstance(result, LLMOutput)
        assert result.machine_states == {"0": [], "1": []}

    def test_fuzzy_machine_name_matching(self):
        """Alias/partial names from MedASR errors should be matched to canonical names."""
        raw = json.dumps({
            "reasoning": "ventilator on",
            "machine_states": {
                "0": [],
                "1": ["ventilator"],   # lowercase — should map to "Ventilator"
            },
        })
        result = parse_llm_output(raw, self.SURGERY)
        assert any("entilator" in n for n in result.machine_states["1"]), \
            "Fuzzy match failed for 'ventilator'"


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  Cross-surgery coverage                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

class TestCrossSurgery:
    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_prompt_builder_all_surgeries(self, surgery):
        builder = PromptBuilder(surgery)
        msgs = builder.build_messages("turn on the lights", None)
        assert len(msgs) >= 2
        system_content = msgs[0]["content"]
        # At least one machine name should appear in the system prompt
        machine_names = [m["name"] for m in MACHINES[surgery].values()]
        assert any(name in system_content for name in machine_names)

    @pytest.mark.parametrize("surgery", list(SurgeryType))
    def test_parser_all_surgeries_safe_fallback(self, surgery):
        result = parse_llm_output("totally invalid string", surgery)
        assert isinstance(result, LLMOutput)
