"""
backend/data
Surgery definitions, machine dictionaries, Pydantic models, and StateManager.

Quick start:
    from backend.data import SurgeryType, StateManager, StateUpdateRequest

    sm  = StateManager(SurgeryType.HEART_TRANSPLANT)
    req = StateUpdateRequest(turn_on=["Patient Monitor", "Ventilator"])
    snap = sm.apply_update(req)
"""

from backend.data.surgeries     import SurgeryType, MACHINES, get_machine_names, get_machines_formatted
from backend.data.models        import ORStateSnapshot, StateUpdateRequest, MachineEntry
from backend.data.state_manager import StateManager

__all__ = [
    "SurgeryType",
    "MACHINES",
    "get_machine_names",
    "get_machines_formatted",
    "ORStateSnapshot",
    "StateUpdateRequest",
    "MachineEntry",
    "StateManager",
]
