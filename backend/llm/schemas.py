"""
backend/llm/schemas.py
Pydantic schema for MedGemma's JSON output.

MedGemma must ALWAYS respond in exactly this structure:
{
  "reasoning": "<single sentence explaining the decision>",
  "machine_states": {
    "0": ["Machine Name A", "Machine Name B"],
    "1": ["Machine Name C"]
  }
}

Key rules enforced here:
  - "0" = machines to turn OFF (only ones changing state)
  - "1" = machines to turn ON (only ones changing state)
  - machine names must be non-empty strings
  - either list can be empty if no change in that direction
"""

from __future__ import annotations
from pydantic import BaseModel, Field, model_validator


class LLMOutput(BaseModel):
    """
    Validated MedGemma output.

    machine_states:
        "0" → list of machine names to switch OFF
        "1" → list of machine names to switch ON
    (Delta only — machines that don't change are NOT listed)
    """
    reasoning:      str              = Field(default="", description="One-sentence reasoning for the decision")
    machine_states: dict[str, list[str]] = Field(
        default_factory=lambda: {"0": [], "1": []},
        description='Keys must be "0" (turn off) and "1" (turn on)',
    )

    @model_validator(mode="after")
    def validate_machine_states(self) -> "LLMOutput":
        ms = self.machine_states
        # Ensure both keys exist
        if "0" not in ms:
            ms["0"] = []
        if "1" not in ms:
            ms["1"] = []
        # Remove any extra keys
        self.machine_states = {"0": ms["0"], "1": ms["1"]}
        # Ensure values are lists of strings
        for key in ("0", "1"):
            if not isinstance(self.machine_states[key], list):
                self.machine_states[key] = []
            self.machine_states[key] = [
                str(v).strip() for v in self.machine_states[key] if str(v).strip()
            ]
        return self

    def to_state_update_kwargs(self) -> dict:
        """Convert to kwargs for StateUpdateRequest construction."""
        return {
            "turn_on":  self.machine_states["1"],
            "turn_off": self.machine_states["0"],
            "reasoning": self.reasoning,
        }
