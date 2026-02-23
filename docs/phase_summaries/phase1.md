# Phase 1 — MedASR Real-Time Transcription

**Status**: ✅ Complete  
**Git Tag**: `v1.0-asr-live`  
**Branch**: `dev` (merged to `main` at tag)

---

## What Was Done in This Phase

Phase 1 brought the first real intelligence into OR-SIM: the ability to listen to a doctor's voice and convert it to text in near real-time, entirely on CPU using the quantized MedASR ONNX model.

### Deliverables

| File | Purpose |
|------|---------|
| `backend/asr/utils.py` | 128-dim log-mel spectrogram extraction from raw 16 kHz PCM |
| `backend/asr/model.py` | ONNX session loader, SentencePiece vocab reader, CTC greedy decoder |
| `backend/asr/audio.py` | Sounddevice microphone capture, ring buffer, sliding-window chunker |
| `backend/asr/transcriber.py` | End-to-end orchestrator, `LiveTranscriber` class, CLI entry point |
| `tests/phase1/test_asr.py` | 20 tests across feature extraction, vocab, model load, inference, latency |

### Test Results (all on CPU, Python 3.11.9)

| Test Group | Result |
|-----------|--------|
| Feature Extraction (6 tests) | ✅ All pass |
| Vocab Loading (4 tests) | ✅ All pass |
| Model Loading (2 tests) | ✅ All pass |
| Inference (5 tests) | ✅ All pass |
| Latency (2 tests) | ✅ All pass |
| Real Audio WAV | ⏭ Skipped (no sample.wav) |

### Latency Measurements (CPU, no GPU)

| Audio Length | Inference Time |
|-------------|---------------|
| 1 second    | **174 ms**     |
| 3 seconds   | **371 ms**     |

These numbers mean the model runs at **~8× real-time speed on CPU alone**. On Kaggle with a T4 GPU, expect < 50 ms per inference call.

---

## What Is Happening in This Phase

Think of Phase 1 as installing and wiring up the "ears" of the OR-SIM system.

1. A microphone captures audio continuously in 20 ms blocks
2. Blocks accumulate in a ring buffer (last 3 seconds of audio always available)
3. Every 0.5 seconds of new speech, the entire 3-second window is extracted
4. The window is converted to a 128-dimensional log-mel spectrogram (time × features matrix)
5. The spectrogram is fed into the MedASR int8 ONNX Conformer CTC model
6. The model outputs token probabilities over 512 vocabulary items for each time step
7. CTC greedy decoding collapses repeated tokens and removes blanks
8. SentencePiece token strings are joined into words using the `▁` space marker
9. The final text is printed with a timestamp and latency reading

---

## Model Architecture (MedASR)

```
[Audio: float32 16kHz]
        │
        ▼
[Log-Mel Spectrogram]  128 bins, 10ms/frame
  shape: [T, 128]
        │
        ▼
[ONNX Conformer CTC — int8]  (model.int8.onnx, ~150MB)
  Input:  x=[1,T,128]  mask=[1,T]
  Output: logits=[1,T/4,512]  logits_len=[1]
        │
        ▼
[CTC Greedy Decode]
  argmax per step → collapse duplicates → remove blanks → join tokens
        │
        ▼
[Text: "turn on the patient monitor"]
```

---

## Visual Flow: Phase 0 → Phase 1

```
Phase 0                 Phase 1
(Foundation)    ──→    (ASR)
   venv                Microphone
   git repo      │       │
   structure      │     AudioCapture (sounddevice)
                  │       │ 20ms blocks → ring buffer
                  │       │ every 0.5s → emit 3s window
                  │       ▼
                  │     utils.py: 128-dim log-mel
                  │       ▼
                  │     model.py: ONNX CTC inference
                  │       ▼
                  │     "turn on the ventilator"
                  └──→  [printed to console with timestamp]
```

---

## How to Run Live Transcription

```bash
cd d:\OR-SIM
venv\Scripts\activate

# List available microphone devices
python -m backend.asr.transcriber --list-devices

# Start live transcription (default microphone)
python -m backend.asr.transcriber

# Use a specific device
python -m backend.asr.transcriber --device 1
```

Expected console output:
```
10:45:01.234  |  INFO     | Initialising MedASR model…
10:45:02.891  |  INFO     | MedASR model loaded. Providers: ['CPUExecutionProvider']
10:45:02.892  |  INFO     | 🎙  Listening… Speak your surgery commands. Press Ctrl+C to stop.
[10:45:05.300]  turn on the patient monitor   (374 ms)
[10:45:08.100]  activate the ventilator   (371 ms)
[10:45:11.400]  turn on the anesthesia machine   (369 ms)
```

---

## Manual Test Before Moving to Phase 2

To validate Phase 1 gives real output (not just passing unit tests):

1. Activate venv: `venv\Scripts\activate`
2. Run: `python -m backend.asr.transcriber`
3. Speak these 5 commands clearly:
   - "turn on the patient monitor"
   - "activate the ventilator"
   - "turn on the anesthesia machine"
   - "turn off the lights"
   - "start the bypass machine"
4. Verify each command appears on screen within 1.5 seconds
5. Latency should be shown in parentheses, ≤ 500ms on CPU

**Only after this manual test passes, proceed to Phase 2.**

---

## What's Next: Phase 2 — Surgery & Machines Data Layer

Phase 2 defines the three surgeries and their complete machine dictionaries, and implements the `StateManager` that tracks which machines are ON/OFF and writes `output/machine_states.json`. This JSON file is the central data contract between the backend pipeline and the future frontend.
