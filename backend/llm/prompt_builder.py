"""
backend/llm/prompt_builder.py
Builds the system prompt and user message for MedGemma.

The system prompt is injected ONCE at session start and contains:
  1. Role definition — OR assistant for the specific surgery
  2. Complete machine list with descriptions and aliases
  3. Strict JSON output schema
  4. Behavioural rules (delta-only, exact names, no extra text)

The user message is built fresh for each transcription and contains:
  - The raw transcription from MedASR
  - Current machine states (what is already ON/OFF)
    so MedGemma can reason without re-reading the full history

Design principles:
  - Be explicit and concrete — MedGemma 4B is small; ambiguity causes errors
  - Keep aliases in the prompt — bridges ASR errors to correct machine names
  - Include current state context — avoids turn-on of already-on machines
  - JSON output schema shown with an example — few-shot helps small models
"""

from __future__ import annotations

import json

from backend.data.surgeries import SurgeryType, MACHINES, get_machines_formatted
from backend.data.models    import ORStateSnapshot


# ── system prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT_TEMPLATE = """\
You are an intelligent operating room control assistant for a {surgery_name} procedure.
Your job is to listen to the surgeon's spoken commands and determine which equipment to turn ON or OFF.

=== AVAILABLE EQUIPMENT ===
{machines_block}

=== MACHINE ALIASES ===
(Alternative names the surgeon may use — map them to the canonical name above)
{aliases_block}

=== YOUR TASK ===
Given the surgeon's latest spoken command, output ONLY a valid JSON object specifying which machines should change state.

IMPORTANT RULES:
1. Use ONLY machine names copied EXACTLY from the numbered list in AVAILABLE EQUIPMENT above.
2. Only list machines that are CHANGING state (delta only — ignore machines already in the correct state).
3. If a command asks to turn something ON, put its EXACT name in "turn_on".
4. If a command asks to turn something OFF, put its EXACT name in "turn_off".
5. If the command is unclear or not equipment-related, return empty lists for both.
6. Output ONLY the JSON. No explanations, no markdown, no code fences.
7. If the surgeon mentions a device that is NOT in the AVAILABLE EQUIPMENT list above (e.g., equipment from a different type of surgery), put its name in "not_available". Do NOT add it to "turn_on" or "turn_off".

=== OUTPUT FORMAT (always use this exact structure) ===
{{
  "reasoning": "<one sentence explaining your decision>",
  "turn_on":       ["<exact canonical name of machine to ACTIVATE>"],
  "turn_off":      ["<exact canonical name of machine to DEACTIVATE>"],
  "not_available": ["<name of any requested device NOT in this surgery's equipment list>"]
}}

=== EXAMPLES ===

Example 1 — Surgeon says: "Activate the bypass machine and turn off the ventilator"
{{
  "reasoning": "Surgeon requested CPB activation and ventilator shutdown as bypass takes over.",
  "turn_on":       ["Cardiopulmonary Bypass Machine"],
  "turn_off":      ["Ventilator"],
  "not_available": []
}}

Example 2 — Surgeon says: "Turn on the OR lights"
{{
  "reasoning": "Surgeon requested surgical lights activation.",
  "turn_on":       ["Surgical Lights"],
  "turn_off":      [],
  "not_available": []
}}

Example 3 — Surgeon says: "We need the defibrillator"
{{
  "reasoning": "Surgeon requested defibrillator readiness — turning it on.",
  "turn_on":       ["Defibrillator"],
  "turn_off":      [],
  "not_available": []
}}

Example 4 — Surgeon says: "Turn everything off"
{{
  "reasoning": "Surgeon requested all equipment to be deactivated.",
  "turn_on":       [],
  "turn_off":      {all_machines_example},
  "not_available": []
}}

Example 5 — Surgeon says: "We need the fluoroscopy C-arm" (not in this surgery's equipment)
{{
  "reasoning": "Fluoroscopy C-Arm is not part of this surgery's equipment list.",
  "turn_on":       [],
  "turn_off":      [],
  "not_available": ["Fluoroscopy C-Arm"]
}}
"""

_USER_MESSAGE_TEMPLATE = """\
=== CURRENT MACHINE STATES ===
Currently ON  : {on_list}
Currently OFF : {off_list}

=== SURGEON'S COMMAND ===
"{transcription}"

Respond with ONLY the JSON object. No other text.\
"""


# ── builder ───────────────────────────────────────────────────────────────────

class PromptBuilder:
    """
    Builds system prompts and user messages for MedGemma.

    Usage
    -----
    builder = PromptBuilder(SurgeryType.HEART_TRANSPLANT)

    # Once:
    system_prompt = builder.build_system_prompt()

    # Per transcription:
    user_msg = builder.build_user_message(transcription, snapshot)
    """

    def __init__(self, surgery: SurgeryType):
        self.surgery = surgery
        self._system_prompt: str | None = None   # cached

    def build_system_prompt(self) -> str:
        """
        Build and cache the system prompt for this surgery session.
        Called once per session start.
        """
        if self._system_prompt is not None:
            return self._system_prompt

        machines = MACHINES[self.surgery]

        # Numbered description block
        machines_block = get_machines_formatted(self.surgery)

        # Aliases block — one line per machine
        alias_lines = []
        for entry in machines.values():
            if entry["aliases"]:
                alias_lines.append(
                    f'  "{entry["name"]}" → also called: '
                    + ", ".join(f'"{a}"' for a in entry["aliases"])
                )
        aliases_block = "\n".join(alias_lines)

        # All machine names as a JSON array literal for the "turn everything off" example
        all_names = [entry["name"] for entry in machines.values()]
        all_machines_example = json.dumps(all_names)

        self._system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            surgery_name          = str(self.surgery),
            machines_block        = machines_block,
            aliases_block         = aliases_block,
            all_machines_example  = all_machines_example,
        )
        return self._system_prompt

    def build_user_message(
        self,
        transcription: str,
        snapshot: ORStateSnapshot | None = None,
    ) -> str:
        """
        Build a user message for a single transcription chunk.

        Parameters
        ----------
        transcription : str            The raw ASR text
        snapshot      : ORStateSnapshot | None
                        Current machine states. If None, states shown as unknown.
        """
        if snapshot is not None:
            on_list  = ", ".join(snapshot.machine_states.get("1", [])) or "None"
            off_list = ", ".join(snapshot.machine_states.get("0", [])) or "None"
        else:
            on_list  = "Unknown (first command)"
            off_list = "Unknown (first command)"

        return _USER_MESSAGE_TEMPLATE.format(
            on_list       = on_list,
            off_list      = off_list,
            transcription = transcription.strip(),
        )

    def build_messages(
        self,
        transcription: str,
        snapshot: ORStateSnapshot | None = None,
    ) -> list[dict]:
        """
        Build the full chat messages list for llama-cpp-python's
        create_chat_completion() API.

        Returns
        -------
        list of {"role": ..., "content": ...} dicts
        """
        return [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user",   "content": self.build_user_message(transcription, snapshot)},
        ]

    def reset(self) -> None:
        """Clear cached system prompt (e.g., on surgery session change)."""
        self._system_prompt = None


# ── CLI self-test ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from backend.data.models import ORStateSnapshot

    print("\n" + "="*70)
    print("  SYSTEM PROMPT — Heart Transplantation")
    print("="*70)
    builder = PromptBuilder(SurgeryType.HEART_TRANSPLANT)
    print(builder.build_system_prompt())

    print("\n" + "="*70)
    print("  USER MESSAGE (first command)")
    print("="*70)
    msg = builder.build_user_message("turn on the patient monitor")
    print(msg)

    print("\n" + "="*70)
    print("  USER MESSAGE (with current state)")
    print("="*70)
    snap = ORStateSnapshot(
        surgery        = "Heart Transplantation",
        machine_states = {
            "0": ["Ventilator", "Cardiopulmonary Bypass Machine"],
            "1": ["Patient Monitor", "Anesthesia Machine"],
        }
    )
    msg2 = builder.build_user_message("now activate the bypass machine", snap)
    print(msg2)
