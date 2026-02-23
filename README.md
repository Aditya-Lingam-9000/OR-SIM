# OR-SIM — Operating Room Simulator

> Real-time intelligent OR simulation: a doctor's spoken commands control a live surgical environment.

## Quick Summary

| Component | Technology | Size |
|-----------|-----------|------|
| Speech → Text | MedASR (ONNX int8) | 150 MB |
| Reasoning | MedGemma 4B Q3_K_M (GGUF) | ~2.1 GB |
| Backend | FastAPI + WebSocket | — |
| Frontend | React + Three.js | — |
| Kaggle GPU | T4 ×2 / P100 (30 GB VRAM) | — |

## Supported Surgeries
1. **Heart Transplantation**
2. **Liver Resection**
3. **Kidney PCNL** (Percutaneous Nephrolithotomy)

## How It Works

```
Mic → MedASR → transcription → MedGemma → machine_states.json → WebSocket → OR Room UI
```

1. Doctor speaks a command during surgery
2. MedASR transcribes speech in near real-time
3. MedGemma reasons about which machines to turn on/off given the surgery context
4. `output/machine_states.json` is updated
5. Frontend OR room reacts: machines glow/dim, animated doctor walks to the machine

## Development Setup

```bash
# 1. Clone
git clone https://github.com/<you>/OR-SIM.git
cd OR-SIM

# 2. Create venv
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/asr.txt

# 4. Place models
# models/medasr/model.int8.onnx
# models/medasr/tokens.txt
# models/medgemma/medgemma-4b-it-Q3_K_M.gguf

# 5. Run ASR test (Phase 1)
python -m backend.asr.transcriber
```

## Kaggle Testing (MedGemma)

```bash
!git clone https://github.com/<you>/OR-SIM.git
!pip install -r OR-SIM/requirements/llm.txt
# Then run: kaggle/phase3_medgemma_test.ipynb
```

## Phase Status
See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for full details.

## Project Structure

```
OR-SIM/
├── backend/        ← Python backend (ASR, LLM, Pipeline, Server)
├── frontend/       ← React + Three.js OR room (Phase 6)
├── kaggle/         ← Kaggle test notebooks
├── models/         ← Local models (gitignored)
├── output/         ← Runtime JSON state (gitignored)
├── tests/          ← Phase-specific tests
├── docs/           ← Phase summary documents
└── requirements/   ← Split requirements files
```
