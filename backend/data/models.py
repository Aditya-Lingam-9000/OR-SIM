"""
backend/data/models.py
Pydantic models for machine states and the full OR state snapshot.

These are the canonical data structures used by StateManager, the FastAPI
server, and the WebSocket broadcaster. They also define the exact schema
written to output/machine_states.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class MachineEntry(BaseModel):
    """Represents a single machine with its operational state."""
    name:        str
    description: str
    is_on:       bool = False


class ORStateSnapshot(BaseModel):
    """
    Full OR state snapshot — written to output/machine_states.json on every update.

    machine_states:
        "0" → list of machine names currently OFF
        "1" → list of machine names currently ON

    This is the contract between backend pipeline and frontend WebSocket.
    """
    surgery:        str
    timestamp:      str   = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    transcription:  str   = ""
    reasoning:      str   = ""
    machine_states: dict[str, list[str]] = Field(
        default_factory=lambda: {"0": [], "1": []}
    )
    # Machine names that were commanded but don't exist in the active surgery.
    # Populated by StateManager.apply_update() so the frontend can warn the user.
    unavailable_machines: list[str] = Field(default_factory=list)

    def to_json_dict(self) -> dict:
        """Return a plain dict suitable for json.dumps."""
        return self.model_dump()


class StateUpdateRequest(BaseModel):
    """
    Request to update machine states — issued by MedGemma output parser.

    turn_on  : list of canonical machine names to switch ON
    turn_off : list of canonical machine names to switch OFF
    """
    turn_on:       list[str] = Field(default_factory=list)
    turn_off:      list[str] = Field(default_factory=list)
    transcription: str       = ""
    reasoning:     str       = ""
