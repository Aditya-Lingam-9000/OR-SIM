"""
backend/asr/model.py
MedASR inference with three-tier fallback.

Model priority
--------------
1. google/medasr PyTorch (local)  — models/medasr/pytorch/ downloaded by Kaggle Cell 6
   Best quality (6.6% WER); loaded from disk, no HF token needed at runtime.
2. sherpa-onnx int8 ONNX          — models/medasr/model.int8.onnx (public, no token)
   Always-available fallback; zero setup required, server never crashes at startup.
3. google/medasr PyTorch (online) — downloaded live from HuggingFace when HF_TOKEN set
   Same quality as Tier 1 but requires a token; used when local copy not present.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

import numpy as np
from loguru import logger

# ── paths ─────────────────────────────────────────────────────────────────────
_MODEL_DIR   = Path(__file__).parent.parent.parent / "models" / "medasr"
_TORCH_DIR   = _MODEL_DIR / "pytorch"          # google/medasr PyTorch local copy (Tier 1)
_INT8_ONNX   = _MODEL_DIR / "model.int8.onnx"  # sherpa-onnx int8 fallback         (Tier 2)
_TOKENS_PATH = _MODEL_DIR / "tokens.txt"
_HF_REPO     = "google/medasr"
SAMPLE_RATE  = 16_000

# ── sherpa-onnx CTC special token IDs ────────────────────────────────────────
_BLANK_ID = 0
_BOS_ID   = 1
_EOS_ID   = 2
_UNK_ID   = 3
_SP_SPACE = "\u2581"   # SentencePiece word-boundary ▁


# ── Tier 2 helpers ────────────────────────────────────────────────────────────

def _load_vocab(tokens_path: Path) -> dict:
    vocab: dict = {}
    try:
        text = tokens_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = tokens_path.read_text(encoding="latin-1")
    for line in text.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        token_text, tid_str = parts
        try:
            vocab[int(tid_str)] = token_text
        except ValueError:
            continue
    return vocab


def _ctc_greedy_decode(logits: np.ndarray, logits_len: np.ndarray, vocab: dict) -> List[str]:
    results = []
    for b in range(logits.shape[0]):
        length     = int(logits_len[b])
        token_ids  = np.argmax(logits[b, :length, :], axis=-1)
        collapsed, prev = [], -1
        for tid in token_ids:
            if tid != prev:
                collapsed.append(int(tid))
            prev = tid
        filtered = [t for t in collapsed if t not in (_BLANK_ID, _BOS_ID, _EOS_ID, _UNK_ID)]
        text = "".join(vocab.get(t, "") for t in filtered)
        text = text.replace(_SP_SPACE, " ").replace("â–", " ").strip()
        text = re.sub(r"\s+", " ", text).strip()
        results.append(text)
    return results


# ── MedASRModel ───────────────────────────────────────────────────────────────

class MedASRModel:
    """
    Unified ASR model with three-tier priority fallback.

    Usage
    -----
    model = MedASRModel()
    text  = model.transcribe(audio_float32_16khz)   # numpy [T], float32, 16 kHz
    """

    def __init__(
        self,
        torch_dir: Optional[Path] = None,
        int8_onnx: Optional[Path] = None,
        hf_token: Optional[str]   = None,
    ):
        self._torch_dir = torch_dir or _TORCH_DIR
        self._int8_path = int8_onnx or _INT8_ONNX
        self._token     = hf_token or os.environ.get("HUGGING_FACE_HUB_TOKEN")

        # Tier 1: google/medasr PyTorch loaded from local directory (no token at runtime)
        if self._torch_dir.exists() and any(self._torch_dir.iterdir()):
            try:
                self._load_torch_local()
                return
            except Exception as exc:
                logger.warning(f"Tier 1 (google/medasr local PyTorch) failed: {exc}")

        # Tier 2: sherpa-onnx int8 ONNX (public, no auth required)
        if self._int8_path.exists():
            try:
                self._load_int8_ort()
                return
            except Exception as exc:
                logger.warning(f"Tier 2 (int8 ONNX) failed: {exc}")

        # Tier 3: google/medasr PyTorch downloaded live (requires HF token)
        if self._token:
            logger.info("Tier 1+2 unavailable; trying Tier 3 (PyTorch google/medasr online)…")
            self._load_torch()
        else:
            raise RuntimeError(
                "No MedASR model available.\n"
                f"  • Tier 1 (google/medasr local): expected at {self._torch_dir} — run Kaggle Cell 6 Part B\n"
                f"  • Tier 2 (int8 ONNX): expected at {self._int8_path} "
                f"(download from csukuangfj/sherpa-onnx-medasr-ctc-en-int8-2025-12-25)\n"
                "  • Tier 3 (PyTorch online): set HUGGING_FACE_HUB_TOKEN env var"
            )

    # ── loaders ───────────────────────────────────────────────────────────────

    @staticmethod
    def _patch_lasr_processor(processor) -> None:
        """
        Fix LasrFeatureExtractor._torch_extract_fbank_features signature mismatch.

        Some transformers versions ship a feature_extraction_lasr.py __call__ that
        calls self._torch_extract_fbank_features(features, device, center) while the
        method itself only accepts (self, features).  Patch the instance to accept
        and ignore the extra positional args so inference doesn't crash.
        """
        import inspect, types
        fe = getattr(processor, "feature_extractor", None)
        if fe is None:
            return
        orig_fn = getattr(fe.__class__, "_torch_extract_fbank_features", None)
        if orig_fn is None:
            return
        sig    = inspect.signature(orig_fn)
        params = list(sig.parameters.keys())   # ['self', 'input_features', ...]
        if len(params) <= 2:
            # __call__ passes extra args (device, center) that the method doesn't accept
            def _patched(self_fe, input_features, *_args, **_kwargs):
                return orig_fn(self_fe, input_features)
            fe._torch_extract_fbank_features = types.MethodType(_patched, fe)
            logger.info("Patched LasrFeatureExtractor._torch_extract_fbank_features (signature mismatch)")

    def _load_torch_local(self) -> None:
        """Tier 1 — google/medasr PyTorch loaded from local directory (no HF token needed)."""
        import torch
        from transformers import AutoModelForCTC, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading google/medasr PyTorch from {self._torch_dir} on {device}…")
        self._processor = AutoProcessor.from_pretrained(str(self._torch_dir))
        self._patch_lasr_processor(self._processor)
        self._model     = AutoModelForCTC.from_pretrained(str(self._torch_dir)).to(device)
        self._device    = device
        self._backend   = "torch_local"
        logger.info(f"MedASR Tier 1 (google/medasr local PyTorch) loaded on {device}")

    def _load_int8_ort(self) -> None:
        """Tier 2 — sherpa-onnx int8 ONNX (public, no auth required)."""
        import onnxruntime as ort

        available = ort.get_available_providers()
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if "CUDAExecutionProvider" in available
            else ["CPUExecutionProvider"]
        )
        logger.info(f"Loading int8 ONNX from {self._int8_path}  providers={providers}")
        self._session = ort.InferenceSession(str(self._int8_path), providers=providers)
        self._vocab   = _load_vocab(_TOKENS_PATH)
        self._backend = "ort_int8"
        logger.info(f"MedASR Tier 2 (sherpa-onnx int8) loaded. Providers: {self._session.get_providers()}")

    def _load_torch(self) -> None:
        """Tier 3 — google/medasr PyTorch downloaded live from HF hub (requires token)."""
        import torch
        from transformers import AutoModelForCTC, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading google/medasr PyTorch (online) on {device}…")
        self._processor = AutoProcessor.from_pretrained(_HF_REPO, token=self._token)
        self._patch_lasr_processor(self._processor)
        self._model     = AutoModelForCTC.from_pretrained(_HF_REPO, token=self._token).to(device)
        self._device    = device
        self._backend   = "torch_google"
        logger.info(f"MedASR Tier 3 (google/medasr PyTorch online) loaded on {device}")

    # ── transcription ─────────────────────────────────────────────────────────

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe a single audio segment.

        Parameters
        ----------
        audio : np.ndarray  shape [num_samples], float32, 16 kHz, range [-1, 1]

        Returns
        -------
        str  transcribed text
        """
        if len(audio) == 0:
            return ""
        if self._backend == "ort_int8":
            return self._transcribe_int8(audio)
        # torch_local (Tier 1) and torch_google (Tier 3) share the same inference path
        return self._transcribe_torch(audio)

    def _transcribe_int8(self, audio: np.ndarray) -> str:
        from backend.asr.utils import audio_to_melfeatures, features_to_model_input

        features           = audio_to_melfeatures(audio)
        x, mask            = features_to_model_input(features)
        logits, logits_len = self._session.run(
            ["logits", "logits_len"], {"x": x, "mask": mask}
        )
        return _ctc_greedy_decode(logits, logits_len, self._vocab)[0]

    def _transcribe_torch(self, audio: np.ndarray) -> str:
        import torch

        inputs = self._processor(audio, sampling_rate=SAMPLE_RATE,
                                  return_tensors="pt", padding=True)
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self._model(**inputs)
        predicted_ids = outputs.logits.argmax(-1)
        return self._processor.batch_decode(predicted_ids)[0].strip().lower()
