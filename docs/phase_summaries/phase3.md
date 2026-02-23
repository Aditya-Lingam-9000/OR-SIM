# Phase 3 Summary — MedGemma LLM Integration

**Tag**: `v3.0-llm-prompt-design`  
**Branch**: `dev`  
**Tests**: 37 / 37 passed (no GPU required)  
**Status**: ✅ Complete (local). Kaggle GPU test pending.

---

## What Was Built

The complete prompt-engineer → inference → parse pipeline for MedGemma 4B.

### Files Created

| File | Purpose |
|------|---------|
| `backend/llm/schemas.py` | `LLMOutput` Pydantic model — validates MedGemma JSON response |
| `backend/llm/prompt_builder.py` | `PromptBuilder` — builds system prompt + user messages per surgery |
| `backend/llm/output_parser.py` | `parse_llm_output()` — robust extraction with 6 fallback strategies |
| `backend/llm/medgemma.py` | `MedGemmaModel` — GGUF inference runner via llama-cpp-python |
| `backend/llm/__init__.py` | Updated exports |
| `tests/phase3/test_llm.py` | 37 unit tests (prompt, schema, parser) |
| `kaggle/phase3_medgemma_test.ipynb` | Kaggle GPU validation notebook (30 samples) |
| `conftest.py` | Root pytest sys.path fixture |

---

## Architecture

```
MedASR transcription
        │
        ▼
PromptBuilder.build_messages(transcription, snapshot)
        │  system prompt: surgery name + 12 machines + aliases + JSON schema + example
        │  user message:  current ON/OFF state + surgeon command
        ▼
MedGemmaModel.infer(transcription, snapshot)
        │  llama-cpp-python create_chat_completion()
        │  temperature=0.1, max_tokens=256
        ▼
parse_llm_output(raw_text, surgery)
        │  6-strategy cascade: direct → code fence → first {..} → trailing comma → quotes
        │  alias-aware normalisation: "bypass pump" → "Cardiopulmonary Bypass Machine"
        ▼
LLMOutput(reasoning, machine_states={"0": [...], "1": [...]})
```

---

## Key Design Decisions

### Alias-Aware Normalisation
MedGemma (and MedASR errors) may output aliases like `"OR Lights"` or `"bypass pump"`.
`_build_alias_map()` builds a lowercase alias → canonical name dict from `MACHINES`.
Resolution order: exact alias match → alias-is-substring → canonical substring.

### 6-Strategy Parser Cascade
1. Direct `json.loads()` — fastest, used for well-formed output
2. Strip markdown code fences (` ```json ... ``` `)
3. Fix trailing commas — common LLM error: `["item",]`
4. Fix trailing commas after code fence strip
5. Extract first `{...}` block (handles preamble text)
6. Fix trailing commas in extracted block

Single-quote fix applied as a separate path for `'key': 'value'` style output.

### Safe Fallback
All parse failures return `LLMOutput(reasoning="...", machine_states={"0":[],"1":[]})` — the pipeline keeps running even if MedGemma outputs garbage.

### GPU Strategy (Kaggle)
- `n_gpu_layers=-1` → all layers on T4 GPU (~2.1 GB VRAM for Q3_K_M)
- `n_ctx=4096` → system prompt + history fits with headroom
- `temperature=0.1` → near-deterministic JSON output
- Target latency: **< 3 seconds** per inference on T4

### Local CPU Dev
- `n_gpu_layers=0` → runs on CPU (~30-60s/call, acceptable for prompt testing)
- `MedGemmaModel = None` if llama-cpp-python not installed — rest of package still imports

---

## Test Coverage

| Class | Tests | Notes |
|-------|-------|-------|
| `TestPromptBuilder` | 11 | All 3 surgeries, caching, message structure |
| `TestLLMOutput` | 6 | Schema validation, to_state_update_kwargs |
| `TestOutputParser` | 8 | 7 edge cases + fuzzy name matching |
| `TestCrossSurgery` | 6 | Parametrized over all 3 SurgeryType values |
| **Total** | **37** | **37/37 passed** |

---

## Known Issues / Limitations

- **No GPU tested locally** — `medgemma.py` and the Kaggle notebook test actual inference;
  the 37 local tests cover prompts and parsing only.
- **ASR errors** — MedASR may output "return on" instead of "turn on";
  MedGemma must infer intent from context. The alias map handles machine name variants.
- **"Turn everything off"** — tested in Kaggle notebook; the prompt example doesn't include
  this case explicitly but MedGemma should generalise from the JSON schema.

---

## Next Phase

**Phase 4 — End-to-End Pipeline**

Connect `LiveTranscriber` → `MedGemmaModel` → `StateManager`:

```python
def on_transcription(text, timestamp):
    snapshot = state_manager.get_snapshot()
    llm_output = medgemma.infer(text, snapshot)
    update = StateUpdateRequest(**llm_output.to_state_update_kwargs(), transcription=text)
    state_manager.apply_update(update)
```

Then add WebSocket broadcast on every `apply_update` callback.
