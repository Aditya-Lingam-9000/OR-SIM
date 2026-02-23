"""
backend/asr/model.py
Loads google/medasr (105M Conformer CTC, trained on >5000 h of medical dictation)
and exposes `MedASRModel.transcribe(audio)` → str.

Model priority
--------------
1. ONNX Runtime via optimum  — loaded from models/medasr/onnx/
   (pre-exported by the Kaggle notebook using optimum exporters)
2. PyTorch via AutoModelForCTC — falls back when no ONNX export is present;
   downloads from HuggingFace using HF_TOKEN if provided.

Why google/medasr over the old int8 sherpa-onnx model
------------------------------------------------------
The old csukuangfj/sherpa-onnx-medasr-ctc-en-int8-2025-12-25 model is INT8-quantized
(~35% smaller than FP32) which introduces phoneme confusion on medical terms
(e.g. "electrocautery" → "electrocatery", "perfusion" → "infusion").
The full-precision google/medasr achieves 6.6% WER vs ~25% for generic ASR on
radiology dictation.
"""

from pathlib import Path
from typing import Optional
import os

import numpy as np
from loguru import logger

# ── paths ─────────────────────────────────────────────────────────────────────
_MODEL_DIR  = Path(__file__).parent.parent.parent / "models" / "medasr"
_ONNX_DIR   = _MODEL_DIR / "onnx"   # pre-exported by Kaggle notebook
_HF_REPO    = "google/medasr"
SAMPLE_RATE = 16_000


class MedASRModel:
    """
    Wraps google/medasr for real-time CTC transcription.

    Priority
    --------
    1. ONNX Runtime (optimum) — fastest, no GPU memory for weights, best for Kaggle
    2. PyTorch (AutoModelForCTC) — fallback used during local development or when
       the ONNX export has not been generated yet

    Usage
    -----
    model = MedASRModel()
    text  = model.transcribe(audio_float32_16khz)  # numpy [T], float32, 16 kHz
    """

    def __init__(
        self,
        onnx_dir: Optional[Path] = None,
        hf_token: Optional[str] = None,
    ):
        self._onnx_dir = onnx_dir or _ONNX_DIR
        # HF token for downloading google/medasr (gated model).
        # Reads from HUGGING_FACE_HUB_TOKEN env var if not passed directly.
        self._token    = hf_token or os.environ.get("HUGGING_FACE_HUB_TOKEN")

        if self._onnx_dir.exists() and any(self._onnx_dir.iterdir()):
            try:
                self._load_ort()
            except Exception as exc:
                logger.warning(
                    f"Failed to load ONNX from {self._onnx_dir} ({exc}). "
                    "Falling back to PyTorch AutoModelForCTC."
                )
                self._load_torch()
        else:
            logger.warning(
                f"ONNX export not found at {self._onnx_dir}. "
                "Falling back to PyTorch AutoModelForCTC.  "
                "Run Kaggle notebook Cell 6 to generate the ONNX export."
            )
            self._load_torch()

    # ── backend loaders ───────────────────────────────────────────────────────

    def _load_ort(self) -> None:
        """Load pre-exported ONNX model via optimum.onnxruntime."""
        from optimum.onnxruntime import ORTModelForCTC
        from transformers import AutoProcessor

        logger.info(f"Loading google/medasr ONNX from {self._onnx_dir}")
        self._processor = AutoProcessor.from_pretrained(str(self._onnx_dir))
        self._model     = ORTModelForCTC.from_pretrained(str(self._onnx_dir))
        self._backend   = "ort"
        logger.info(f"MedASR ORT model loaded  (providers: {self._model.providers})")

    def _load_torch(self) -> None:
        """Load google/medasr via PyTorch (requires HF token for gated model)."""
        import torch
        from transformers import AutoModelForCTC, AutoProcessor

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Loading google/medasr via torch on {device}  (repo={_HF_REPO})")

        self._processor = AutoProcessor.from_pretrained(
            _HF_REPO, token=self._token
        )
        self._model = (
            AutoModelForCTC.from_pretrained(_HF_REPO, token=self._token)
            .to(device)
        )
        self._device  = device
        self._backend = "torch"
        logger.info(f"MedASR torch model loaded on {device}")

    # ── transcription ─────────────────────────────────────────────────────────

    def transcribe(self, audio: np.ndarray) -> str:
        """
        Transcribe a single audio segment.

        Parameters
        ----------
        audio : np.ndarray  shape [num_samples], float32, 16 kHz, range [-1, 1]

        Returns
        -------
        str  lower-cased transcribed text, empty string if audio is silent/too short
        """
        if len(audio) == 0:
            return ""
        if self._backend == "ort":
            return self._transcribe_ort(audio)
        return self._transcribe_torch(audio)

    def _transcribe_ort(self, audio: np.ndarray) -> str:
        inputs = self._processor(
            audio,
            sampling_rate=SAMPLE_RATE,
            return_tensors="pt",
            padding=True,
        )
        outputs       = self._model(**inputs)
        predicted_ids = outputs.logits.argmax(-1)
        text          = self._processor.batch_decode(predicted_ids)[0]
        return text.strip().lower()

    def _transcribe_torch(self, audio: np.ndarray) -> str:
        import torch

        inputs = self._processor(
            audio,
            sampling_rate=SAMPLE_RATE,
            return_tensors="pt",
            padding=True,
        )
        inputs = {k: v.to(self._device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self._model(**inputs)
        predicted_ids = outputs.logits.argmax(-1)
        text          = self._processor.batch_decode(predicted_ids)[0]
        return text.strip().lower()
