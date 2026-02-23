# Phase 2 — Surgery & Machines Data Layer

**Status**: ✅ Complete  
**Git Tag**: `v2.0-data-layer`  
**Branch**: `dev`

---

## What Was Done in This Phase

Phase 2 defines the complete data contract for the entire OR-SIM system. Every piece of information about surgeries and their machines is encoded here — names, descriptions, aliases — and the `StateManager` is the single source of truth for what is ON or OFF at any moment.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/data/surgeries.py` | `SurgeryType` enum + complete `MACHINES` dict for all 3 surgeries (12 machines each) |
| `backend/data/models.py` | Pydantic models: `ORStateSnapshot`, `StateUpdateRequest`, `MachineEntry` |
| `backend/data/state_manager.py` | `StateManager` class — tracks ON/OFF state, atomic JSON writer, thread-safe, callback support |
| `tests/phase2/test_data.py` | **52 tests** — enum, dictionaries, models, state transitions, fuzzy resolution, thread safety |

### Test Results

| Test Group | Count | Result |
|-----------|-------|--------|
| Surgery enum | 4 | ✅ |
| Machine dictionaries | 15 | ✅ |
| Pydantic models | 5 | ✅ |
| StateManager init | 4 | ✅ |
| State transitions | 8 | ✅ |
| Fuzzy name resolution | 3 | ✅ |
| JSON file integrity | 3 | ✅ |
| Thread safety | 1 | ✅ |
| Callbacks | 2 | ✅ |
| **Total** | **52** | **✅ All pass** |

---

## What Is Happening in This Phase

Think of Phase 2 as building the **equipment manifest and control panel** for the operating room.

1. **`surgeries.py`** — defines exactly what equipment each surgery uses, with descriptions MedGemma will read and aliases to help it understand when the doctor says "bypass" vs "Cardiopulmonary Bypass Machine"
2. **`models.py`** — defines the JSON schema that flows between backend and frontend
3. **`state_manager.py`** — maintains a live `{machine_name: is_on}` dictionary, applies updates atomically, and writes `output/machine_states.json` after every change

---

## Machine Dictionaries Summary

| Surgery | Machines |
|---------|---------|
| Heart Transplantation | Patient Monitor, Ventilator, Anesthesia Machine, Cardiopulmonary Bypass Machine, Perfusion Pump, Defibrillator, Electrocautery Unit, Suction Device, Blood Warmer, Warming Blanket, Surgical Lights, Instrument Table |
| Liver Resection | Patient Monitor, Ventilator, Anesthesia Machine, Electrocautery Unit, Argon Beam Coagulator, Ultrasonic Dissector (CUSA), Suction Device, Cell Saver, Fluid Warmer, Laparoscopy Tower, CO2 Insufflator, Surgical Lights |
| Kidney PCNL | Patient Monitor, Fluoroscopy C-Arm, Nephroscope Unit, Lithotripsy Device, Irrigation Pump, Suction Device, Anesthesia Machine, Surgical Lights, Electrocautery Unit, Contrast Injector, Video Tower, Stone Retrieval System |

---

## JSON Output Format (`output/machine_states.json`)

```json
{
  "surgery": "Heart Transplantation",
  "timestamp": "2026-02-23T02:13:37.993129+00:00",
  "transcription": "start the bypass machine and stop the ventilator",
  "reasoning": "CPB taking over — lungs bypassed",
  "machine_states": {
    "0": ["Ventilator", "Defibrillator", "Electrocautery Unit", ...],
    "1": ["Patient Monitor", "Anesthesia Machine", "Cardiopulmonary Bypass Machine", ...]
  }
}
```
- Written **atomically** (`write to .tmp → os.replace()`) — frontend never reads a partial file
- Updated on **every state change** (will be sub-second in Phase 4)
- **Thread-safe** — lock guards all mutations

---

## Visual Flow: Phase 0 → Phase 1 → Phase 2

```
Phase 0          Phase 1             Phase 2
(Foundation) → (ASR Live)       → (Data Layer)
  venv          Microphone            SurgeryType enum
  git repo        │                   MACHINES dict (3 × 12)
  structure       ▼                      │
               AudioCapture              │ on session start
               (VAD detect)              ▼
                  │              StateManager.init()
                  ▼                → all 12 OFF
               MedASR ONNX           → write JSON
                  │                      │
                  ▼                      │ on every update
               "turn on the          StateUpdateRequest
                ventilator"     →   .apply_update()
                                    → turn_on: [Ventilator]
                                    → write JSON atomically
                                    → fire callbacks
```

---

## Key Design Decisions

**Fuzzy name resolution in `_resolve_name()`**:
- Exact match → case-insensitive match → partial substring match
- This means MedGemma can output "bypass" and it maps to "Cardiopulmonary Bypass Machine"
- Also handles the transcription errors from MedASR (Phase 3 will improve this further)

**Aliases on every machine**:
- Each machine entry contains a list of common shorthand names
- These aliases will be injected into the MedGemma system prompt so the model knows "bovie" means "Electrocautery Unit"

---

## Manual Verification

```bash
# See all 3 surgery machine lists:
venv\Scripts\python.exe -m backend.data.surgeries

# Watch StateManager run through 3 state transitions and write JSON:
venv\Scripts\python.exe -m backend.data.state_manager

# Inspect the output JSON:
Get-Content output\machine_states.json
```

---

## What's Next: Phase 3 — MedGemma Prompt Design + Kaggle Testing

Phase 3 designs the exact system prompt that MedGemma receives (surgery name + full machine dict with aliases + output schema), implements the output JSON parser, and validates it all on Kaggle with a T4 GPU.

**First Kaggle test**: 10 sample transcriptions per surgery → verify MedGemma outputs valid JSON with correct machine names matching the dictionary.
