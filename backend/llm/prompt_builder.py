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
1. Only list machines that are CHANGING state (delta only — do not repeat machines already in their correct state).
2. Machine names in your output MUST match EXACTLY the canonical names listed in AVAILABLE EQUIPMENT.
3. If the command is unclear or not equipment-related, return empty lists.
4. Do NOT output anything outside the JSON block — no explanations, no markdown, no code fences.
5. The JSON must have exactly two keys: "reasoning" and "machine_states".

=== OUTPUT FORMAT (always use this exact structure) ===
{{
  "reasoning": "<one sentence explaining your decision>",
  "machine_states": {{
    "0": ["<canonical machine name to turn OFF>", ...],
    "1": ["<canonical machine name to turn ON>", ...]
  }}
}}

=== EXAMPLE ===
Surgeon says: "Activate the bypass machine and turn off the ventilator"
Correct output:
{{
  "reasoning": "Surgeon requested CPB activation and ventilator shutdown as bypass takes over lung function.",
  "machine_states": {{
    "0": ["Ventilator"],
    "1": ["Cardiopulmonary Bypass Machine"]
  }}
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

        self._system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
            surgery_name   = str(self.surgery),
            machines_block = machines_block,
            aliases_block  = aliases_block,
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
