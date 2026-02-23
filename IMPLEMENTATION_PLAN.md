# OR-SIM: Operating Room Simulator — Implementation Plan

> **Project Vision**: A real-time intelligent operating room simulator where a doctor's spoken commands
> (captured via microphone) are transcribed by MedASR, reasoned about by MedGemma, and used to
> dynamically control a 3D OR visualization — turning machines on/off, adjusting lighting, and
> animating surgical staff — all within a fraction of a second.

---

## Architecture Overview

```
[Microphone]
     │
     ▼
[MedASR ONNX — int8]          ← models/medasr/model.int8.onnx
     │  live transcription
     ▼
[MedGemma 4B Q3_K_M]          ← models/medgemma/medgemma-4b-it-Q3_K_M.gguf
     │  system_prompt(surgery) + transcription + machines_dict
     ▼
[output/machine_states.json]   ← continuously updated JSON {0: [...off], 1: [...on]}
     │
     ▼
[FastAPI WebSocket Server]
     │
     ▼
[Frontend — 3D OR Room Viz]    ← Three.js / Canvas, surgery-specific environment
     └─ machines toggle on/off, lights, animated doctors respond live
```

---

## Surgery Types & Machine Dictionaries (Phase 2)

### 1. Heart Transplantation
- Patient Monitor, Ventilator, Cardiopulmonary Bypass Machine, Defibrillator,
  Electrocautery Unit, Suction Device, Warming Blanket, Anesthesia Machine,
  Perfusion Pump, Surgical Lights, Instrument Table, Blood Warmer

### 2. Liver Resection
- Patient Monitor, Ventilator, Anesthesia Machine, Electrocautery Unit,
  Argon Beam Coagulator, Suction Device, Ultrasonic Dissector (CUSA),
  Surgical Lights, Cell Saver, Fluid Warmer, Laparoscopy Tower, CO2 Insufflator

### 3. Kidney PCNL (Percutaneous Nephrolithotomy)
- Patient Monitor, Fluoroscopy C-Arm, Nephroscope Unit, Lithotripsy Device,
  Irrigation Pump, Suction Device, Anesthesia Machine, Surgical Lights,
  Electrocautery Unit, Contrast Injector, Video Tower, Stone Retrieval System

---

## JSON Machine State Format

```json
{
  "surgery": "Heart Transplantation",
  "timestamp": "2026-02-23T10:45:00.123Z",
  "transcription": "Turn on the cardiopulmonary bypass machine",
  "reasoning": "Doctor instructed activation of bypass machine during surgery",
  "machine_states": {
    "0": ["Ventilator", "Surgical Lights"],
    "1": ["Patient Monitor", "Anesthesia Machine", "Cardiopulmonary Bypass Machine"]
  }
}
```
- Key `"0"` → machines currently **OFF**
- Key `"1"` → machines currently **ON**
- This file is **overwritten on every update** → frontend polls / WebSocket pushes delta

---

## Development Phases

---

### PHASE 0 — Project Foundation
**Goal**: Clean, reproducible dev environment with version control.

#### Sub-phases:
- [x] 0.1 Create virtual environment (`venv`)
- [x] 0.2 Initialize Git repo locally
- [x] 0.3 Create GitHub repository & push initial commit
- [x] 0.4 Create `.gitignore` (models, venv, __pycache__, output runtime files)
- [x] 0.5 Create base `requirements.txt`
- [x] 0.6 Create project folder skeleton

#### Folder Structure:
```
OR-SIM/
├── .gitignore
├── README.md
├── IMPLEMENTATION_PLAN.md
├── requirements/
│   ├── base.txt          ← common deps
│   ├── asr.txt           ← MedASR specific
│   ├── llm.txt           ← MedGemma / llama-cpp specific
│   └── dev.txt           ← testing, linting
├── models/               ← GITIGNORED (large files)
│   ├── medasr/
│   └── medgemma/
├── backend/
│   ├── asr/              ← Phase 1
│   ├── data/             ← Phase 2
│   ├── llm/              ← Phase 3–4
│   ├── pipeline/         ← Phase 5
│   └── server/           ← Phase 6
├── output/               ← runtime JSON (gitignored during dev)
├── logs/
├── kaggle/               ← Kaggle notebooks for MedGemma testing
├── tests/
│   ├── phase1/
│   ├── phase2/
│   └── phase3/
├── docs/
│   └── phase_summaries/  ← one .md per completed phase
└── frontend/             ← Phase 7 (last)
```

#### Sanity Check:
```bash
python --version          # should be 3.10+
git status                # clean working tree
pip list                  # confirm base packages installed
```

#### Git Tag: `v0.0-foundation`

---

### PHASE 1 — MedASR Real-Time Transcription
**Goal**: Speak into mic → see accurate text on console within ~1 second.

#### Sub-phases:
- [ ] 1.1 Install and validate ONNX Runtime + audio deps
- [ ] 1.2 Load `model.int8.onnx` + `tokens.txt` → verify model loads
- [ ] 1.3 Implement audio capture loop (`sounddevice`, 16kHz, mono, float32)
- [ ] 1.4 Implement chunked inference: sliding window (e.g. 1s chunks, 0.25s stride)
- [ ] 1.5 Implement greedy/beam decode → text using `tokens.txt`
- [ ] 1.6 Accumulate and print live transcription with timestamps
- [ ] 1.7 Write unit test: feed recorded .wav → compare expected text

#### Key Files:
```
backend/asr/
├── __init__.py
├── model.py          ← load ONNX model, tokenizer
├── audio.py          ← microphone capture, chunking
├── transcriber.py    ← inference loop, decode, callback
└── utils.py          ← audio preprocessing (resample, normalize)
tests/phase1/
└── test_asr.py
```

#### Expected Output (console):
```
[00:00.000] Turn on the patient monitor
[00:02.450] Now activate the ventilator
[00:04.100] Turn on the anesthesia machine
```

#### Sanity / Manual Test:
1. Run `python -m backend.asr.transcriber`
2. Speak 5 surgery commands into mic
3. Verify text appears within ≤ 1.5 seconds of speaking
4. Confirm no crashes over 60 seconds of continuous audio

#### Git Tag: `v1.0-asr-live`

---

### PHASE 2 — Surgery & Machines Data Layer
**Goal**: A clean, importable data module with all 3 surgeries and their machine dictionaries.

#### Sub-phases:
- [ ] 2.1 Define `SurgeryType` enum (`HEART_TRANSPLANT`, `LIVER_RESECTION`, `KIDNEY_PCNL`)
- [ ] 2.2 Build machines dictionary for Heart Transplantation
- [ ] 2.3 Build machines dictionary for Liver Resection
- [ ] 2.4 Build machines dictionary for Kidney PCNL
- [ ] 2.5 Define `MachineState` and `ORState` Pydantic models
- [ ] 2.6 Implement `StateManager` — tracks current on/off states, serializes to JSON
- [ ] 2.7 Implement `output/machine_states.json` writer with atomic file write
- [ ] 2.8 Unit tests for state transitions

#### Machine Dictionary Format:
```python
MACHINES = {
    SurgeryType.HEART_TRANSPLANT: {
        0: {"name": "Patient Monitor",     "description": "Monitors vitals: HR, BP, SpO2, ECG continuously"},
        1: {"name": "Ventilator",           "description": "Controls mechanical breathing via ETT"},
        2: {"name": "Anesthesia Machine",   "description": "Delivers inhalational anesthetics and O2"},
        ...
    }
}
```

#### Key Files:
```
backend/data/
├── __init__.py
├── surgeries.py      ← MACHINES dict, SurgeryType enum
├── models.py         ← Pydantic: MachineState, ORState
└── state_manager.py  ← StateManager class
tests/phase2/
└── test_data.py
```

#### Expected Output:
```bash
python -m backend.data.surgeries
# Prints all 3 surgeries with machine count
# Heart Transplantation: 12 machines
# Liver Resection: 12 machines
# Kidney PCNL: 12 machines

python -m backend.data.state_manager
# Simulates 3 state transitions → writes output/machine_states.json
# Prints diff after each transition
```

#### Git Tag: `v2.0-data-layer`

---

### PHASE 3 — MedGemma System Prompt & I/O Design
**Goal**: Design + validate the exact prompts and I/O contract for MedGemma — ensuring reliable JSON output.

#### Sub-phases:
- [ ] 3.1 Design system prompt template (surgery name + machines dict injected)
- [ ] 3.2 Design user message format (latest transcription chunk)
- [ ] 3.3 Define exact JSON output schema MedGemma must follow
- [ ] 3.4 Implement prompt builder (`PromptBuilder` class)
- [ ] 3.5 Implement JSON output parser + validator with fallback/retry logic
- [ ] 3.6 Create Kaggle notebook skeleton (`kaggle/phase3_medgemma_test.ipynb`)
- [ ] 3.7 **[KAGGLE TEST]** — Clone repo, run notebook, validate JSON output manually

#### System Prompt Template:
```
You are an intelligent operating room assistant for a {surgery_name} procedure.

AVAILABLE MACHINES:
{machines_dict_formatted}

Your role: Based on the surgeon's spoken instruction, determine which machines should be ON and which should be OFF.

ALWAYS respond ONLY in this exact JSON format:
{
  "reasoning": "<1 sentence explaining your decision>",
  "machine_states": {
    "0": ["<machine names to turn OFF>"],
    "1": ["<machine names to turn ON>"]
  }
}

Rules:
- Only include machines that CHANGE state in this turn
- Machine names must match exactly from the AVAILABLE MACHINES list
- Do not add any text outside the JSON block
```

#### Key Files:
```
backend/llm/
├── __init__.py
├── prompt_builder.py    ← builds system + user prompts
├── medgemma.py          ← loads GGUF, runs inference (llama-cpp-python)
├── output_parser.py     ← extracts + validates JSON from LLM response
└── schemas.py           ← Pydantic schema for LLM output
kaggle/
└── phase3_medgemma_test.ipynb
```

#### Kaggle Test Protocol:
1. Push Phase 3 code to GitHub
2. On Kaggle (T4x2/P100): `git clone <repo>`
3. Install deps: `pip install -r requirements/llm.txt`
4. Run notebook with 10 sample transcriptions per surgery
5. Verify JSON output is valid, machine names match dict, reasoning is sensible
6. Measure inference time per call (target: < 3 seconds on T4)

#### Git Tag: `v3.0-llm-prompt-design`

---

### PHASE 4 — End-to-End Pipeline (ASR → MedGemma → JSON)
**Goal**: Speak a command → JSON file updated with correct machine states within a few seconds.

#### Sub-phases:
- [ ] 4.1 Implement `PipelineOrchestrator` connecting ASR → MedGemma → StateManager
- [ ] 4.2 Implement async queue between ASR and LLM (avoid blocking audio capture)
- [ ] 4.3 Implement continuous `output/machine_states.json` overwrite loop
- [ ] 4.4 Implement latency measurement (ASR end → JSON write timestamp)
- [ ] 4.5 Optimize: batch short utterances, skip silence, debounce
- [ ] 4.6 **[KAGGLE TEST]** — Full pipeline notebook with live microphone (or pre-recorded audio)
- [ ] 4.7 Validate: 10 commands, measure average end-to-end latency
- [ ] 4.8 Optimize GPU utilization (target: use both T4s via model parallelism or batching)

#### Key Files:
```
backend/pipeline/
├── __init__.py
├── orchestrator.py   ← PipelineOrchestrator: ties ASR + LLM + StateManager
├── queue.py          ← async queue for ASR→LLM handoff
└── latency.py        ← latency tracker / logger
kaggle/
└── phase4_pipeline_test.ipynb
```

#### Expected Console Output:
```
[Pipeline] Surgery: Heart Transplantation
[ASR 00:01.2] "Turn on the patient monitor"
[LLM 00:02.8] States updated → ON: [Patient Monitor]  (latency: 1.6s)
[ASR 00:04.0] "Activate the bypass machine"
[LLM 00:05.3] States updated → ON: [Cardiopulmonary Bypass Machine]  (latency: 1.3s)
```

#### JSON output after 2 commands:
```json
{
  "surgery": "Heart Transplantation",
  "timestamp": "...",
  "machine_states": { "0": [...], "1": ["Patient Monitor", "Cardiopulmonary Bypass Machine"] }
}
```

#### Git Tag: `v4.0-pipeline-e2e`

---

### PHASE 5 — FastAPI Backend Server + WebSocket
**Goal**: Expose the pipeline over HTTP + WebSocket so the frontend can connect and receive live updates.

#### Sub-phases:
- [ ] 5.1 Create FastAPI app with lifespan — start pipeline on startup
- [ ] 5.2 `POST /api/session/start` — accepts `surgery_type`, initializes pipeline
- [ ] 5.3 `POST /api/session/stop` — gracefully shuts down pipeline
- [ ] 5.4 `GET /api/state` — returns current machine state JSON (REST polling fallback)
- [ ] 5.5 `WS /ws/state` — WebSocket that pushes state diffs on every JSON update
- [ ] 5.6 File watcher on `output/machine_states.json` → triggers WebSocket broadcast
- [ ] 5.7 CORS setup for local frontend dev
- [ ] 5.8 Manual test: WebSocket client script + curl tests

#### Key Files:
```
backend/server/
├── __init__.py
├── app.py          ← FastAPI app, lifespan, cors
├── routes.py       ← REST endpoints
├── websocket.py    ← WS manager, broadcaster
└── watcher.py      ← watchdog file watcher → triggers WS broadcast
```

#### Test with:
```bash
# Terminal 1
uvicorn backend.server.app:app --reload

# Terminal 2
python tests/phase5/ws_client_test.py  # connects to WS, prints received updates

# Terminal 3
python -m backend.asr.transcriber      # speak commands → watch Terminal 2 update
```

#### Git Tag: `v5.0-backend-server`

---

### PHASE 6 — Frontend: OR Room Visualization
**Goal**: A browser-based 3D/2D surgical OR room that reacts live to machine state changes.

> **This phase begins ONLY after Phase 5 is fully validated end-to-end.**

#### Sub-phases:
- [ ] 6.1 Setup frontend scaffold (Vite + React + Three.js or PixiJS)
- [ ] 6.2 Surgery selection dropdown (3 types)
- [ ] 6.3 Per-surgery OR room scene with:
  - Surgical bed + patient model
  - All machines placed in anatomically correct positions
  - Overhead surgical lights
  - 2 animated doctor/nurse characters
- [ ] 6.4 WebSocket client integration — connect to `WS /ws/state`
- [ ] 6.5 Machine state renderer:
  - Machine ON → glowing green indicator, active animation
  - Machine OFF → dim gray, idle
- [ ] 6.6 Animated agent behavior:
  - On machine turn-on event → doctor character walks to machine, activates it
  - On machine turn-off event → doctor turns it off and returns
- [ ] 6.7 Light switching (surgical lights on/off)
- [ ] 6.8 Transcription live caption overlay at bottom of screen
- [ ] 6.9 Surgery-specific OR room assets (3 different room layouts)
- [ ] 6.10 Performance: smooth 60fps even during WS updates

#### Key Files:
```
frontend/
├── index.html
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── components/
│   │   ├── SurgerySelector.jsx
│   │   ├── ORRoom.jsx            ← Three.js/PixiJS canvas
│   │   ├── MachineNode.jsx       ← individual machine component
│   │   └── TranscriptionBar.jsx  ← live caption strip
│   ├── scenes/
│   │   ├── HeartTransplantRoom.js
│   │   ├── LiverResectionRoom.js
│   │   └── KidneyPCNLRoom.js
│   ├── hooks/
│   │   └── useORWebSocket.js      ← WS connection hook
│   └── store/
│       └── machineStore.js        ← Zustand state
└── public/
    └── assets/                    ← room models, textures
```

#### Git Tag: `v6.0-frontend-or-room`

---

## Phase Completion Checklist Template

After each phase, before moving to the next:

| Check | Status |
|-------|--------|
| All sub-phases marked done | ☐ |
| Unit tests pass | ☐ |
| Manual real-output test passed | ☐ |
| Phase summary doc written (`docs/phase_summaries/phaseN.md`) | ☐ |
| `.gitignore` reviewed and updated | ☐ |
| Git tag pushed | ☐ |
| Requirements files updated | ☐ |

---

## Kaggle Usage Protocol

MedGemma testing happens only on Kaggle (no local GPU):

1. Push latest code to GitHub
2. On Kaggle: `!git clone https://github.com/<you>/OR-SIM.git`
3. `!pip install -r OR-SIM/requirements/llm.txt`
4. Mount model: upload `.gguf` to Kaggle datasets OR copy from Kaggle's model hub
5. Run test notebook
6. Copy results (latency measurements, sample outputs) back to `docs/`
7. Commit findings

**GPU Strategy for Kaggle T4x2 (30GB total VRAM):**
- MedGemma 4B Q3_K_M ≈ 2.1 GB → fits easily on single T4
- MedASR int8 ONNX ≈ 150 MB → assign to CPU or second GPU
- Set `n_gpu_layers=-1` in llama-cpp to use all layers on GPU
- Use `n_threads=4` for CPU-side tokenization
- Enable `use_mlock=True` to prevent swapping

---

## Git Strategy

```
main         ← stable, phase-complete code
dev          ← active development
phase/N-xxx  ← feature branches per phase
```

```bash
# After each phase
git checkout main
git merge dev
git tag vN.0-phase-name
git push origin main --tags
```

---

## Requirements Summary

### requirements/base.txt
```
pydantic>=2.0
python-dotenv
loguru
watchdog
```

### requirements/asr.txt
```
onnxruntime>=1.17
sounddevice
numpy
scipy
```

### requirements/llm.txt
```
llama-cpp-python  (with CUDA)
```

### requirements/server.txt
```
fastapi
uvicorn[standard]
websockets
python-multipart
```

### requirements/dev.txt
```
pytest
pytest-asyncio
black
ruff
```

---

## Current Status

| Phase | Status | Git Tag |
|-------|--------|---------|
| Phase 0 — Foundation | ✅ Complete | `v0.0-foundation` |
| Phase 1 — MedASR | ✅ Complete | `v1.0-asr-live` |
| Phase 2 — Data Layer | ⏳ Not Started | — |
| Phase 3 — LLM Prompts (Kaggle) | ⏳ Not Started | — |
| Phase 4 — E2E Pipeline (Kaggle) | ⏳ Not Started | — |
| Phase 5 — Backend Server | ⏳ Not Started | — |
| Phase 6 — Frontend | ⏳ Not Started | — |

---

*This document will be updated at the completion of each phase.*
