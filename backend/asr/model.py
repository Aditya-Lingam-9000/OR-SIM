"""
backend/asr/model.py
Loads the MedASR int8 ONNX Conformer model and the SentencePiece-style tokens.txt
vocabulary. Exposes `MedASRModel.transcribe(audio)` which returns decoded text.

tokens.txt format: one token per line — "<token_text> <token_id>"
  Token 0 = <blk>  (CTC blank)
  Token 1 = <s>    (BOS — unused in greedy decode)
  Token 2 = </s>   (EOS)
  Token 3 = <unk>
  Token 4 = ▁      (SentencePiece word-boundary space)
  ...
"""

import re
from pathlib import Path
from typing import List, Optional

import numpy as np
import onnxruntime as ort
from loguru import logger

from backend.asr.utils import audio_to_melfeatures, features_to_model_input

# ── paths ─────────────────────────────────────────────────────────────────────
_MODEL_DIR   = Path(__file__).parent.parent.parent / "models" / "medasr"
_ONNX_PATH   = _MODEL_DIR / "model.int8.onnx"
_TOKENS_PATH = _MODEL_DIR / "tokens.txt"

# ── CTC blank & special token IDs ────────────────────────────────────────────
BLANK_ID = 0
BOS_ID   = 1
EOS_ID   = 2
UNK_ID   = 3

# SentencePiece word-boundary marker (▁, UTF-8: E2 96 81)
SP_SPACE = "\u2581"   # ▁


# ── tokenizer ────────────────────────────────────────────────────────────────

def load_vocab(tokens_path: Path) -> dict:
    """
    Parse tokens.txt into {token_id: token_text} mapping.
    Handles both UTF-8 and latin-1 encoded files.
    """
    vocab: dict = {}
    try:
        text = tokens_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = tokens_path.read_text(encoding="latin-1")

    for line in text.splitlines():
        line = line.rstrip("\n")
        if not line:
            continue
        # Format: "<token_text> <token_id>"
        # Split from the RIGHT so tokens containing spaces are preserved
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        token_text, token_id_str = parts
        try:
            token_id = int(token_id_str)
        except ValueError:
            continue
        vocab[token_id] = token_text

    logger.debug(f"Loaded vocab: {len(vocab)} tokens from {tokens_path}")
    return vocab


def ctc_greedy_decode(logits: np.ndarray, logits_len: np.ndarray, vocab: dict) -> List[str]:
    """
    CTC greedy decode for a batch of logit sequences.

    Parameters
    ----------
    logits     : np.ndarray  [N, T_out, vocab_size]
    logits_len : np.ndarray  [N]  actual output lengths
    vocab      : dict        {id: text}

    Returns
    -------
    List[str]  decoded text for each item in the batch
    """
    results = []
    batch_size = logits.shape[0]

    for b in range(batch_size):
        length   = int(logits_len[b])
        seq_logits = logits[b, :length, :]            # [T_out, vocab_size]
        token_ids  = np.argmax(seq_logits, axis=-1)   # [T_out]

        # CTC collapse: remove consecutive duplicates, then remove blank
        collapsed = []
        prev_id   = -1
        for tid in token_ids:
            if tid != prev_id:
                collapsed.append(int(tid))
            prev_id = tid

        # Filter blanks and special tokens (BOS, EOS, UNK)
        filtered = [tid for tid in collapsed
                    if tid not in (BLANK_ID, BOS_ID, EOS_ID, UNK_ID)]

        # Map IDs → token texts
        tokens = [vocab.get(tid, "<?>") for tid in filtered]

        # Join SentencePiece tokens into words
        # ▁ marks the start of a new word → replace with space
        text = "".join(tokens)
        text = text.replace(SP_SPACE, " ").strip()

        # Also handle the mojibake version (â–) in case file was latin-1 encoded
        text = text.replace("â–", " ").strip()

        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()

        results.append(text)

    return results


# ── model ─────────────────────────────────────────────────────────────────────

class MedASRModel:
    """
    Loads and runs the MedASR int8 ONNX Conformer CTC model.

    Usage
    -----
    model = MedASRModel()
    text  = model.transcribe(audio_float32_16khz)
    """

    def __init__(
        self,
        onnx_path: Optional[Path] = None,
        tokens_path: Optional[Path] = None,
        providers: Optional[List[str]] = None,
    ):
        self.onnx_path   = onnx_path   or _ONNX_PATH
        self.tokens_path = tokens_path or _TOKENS_PATH

        # Prefer CUDA if available, fall back to CPU
        if providers is None:
            available = [p for p in ort.get_available_providers()]
            logger.debug(f"Available ORT providers: {available}")
            if "CUDAExecutionProvider" in available:
                providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            else:
                providers = ["CPUExecutionProvider"]

        logger.info(f"Loading MedASR model from {self.onnx_path}")
        self._session = ort.InferenceSession(
            str(self.onnx_path),
            providers=providers,
        )
        logger.info(f"MedASR model loaded. Providers: {self._session.get_providers()}")

        self._vocab = load_vocab(self.tokens_path)

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

        features     = audio_to_melfeatures(audio)
        x, mask      = features_to_model_input(features)

        outputs      = self._session.run(
            ["logits", "logits_len"],
            {"x": x, "mask": mask},
        )
        logits      = outputs[0]   # [1, T_out, 512]
        logits_len  = outputs[1]   # [1]

        texts = ctc_greedy_decode(logits, logits_len, self._vocab)
        return texts[0]
