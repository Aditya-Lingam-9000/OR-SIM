"""
backend/llm/medgemma.py
MedGemma 4B Q3_K_M inference via llama-cpp-python.

Model: medgemma-4b-it-Q3_K_M.gguf (~2.1 GB)
Architecture: Gemma 2 instruction-tuned, 4B parameters, 3-bit quantised

GPU strategy (Kaggle T4x2 / P100 — 30 GB VRAM):
  medgemma-4b-it-Q3_K_M ≈ 2.1 GB → fits on a single T4 with n_gpu_layers=-1
  MedASR int8 ONNX       ≈ 150 MB  → CPU (ONNX Runtime)
  Remaining VRAM: ~15 GB → available for KV cache (n_ctx=4096)

Local CPU (dev machine, no GPU):
  llama-cpp-python runs on CPU — slow (~30-60s/call) but works for testing prompts
  Set n_gpu_layers=0 explicitly or let it auto-detect

Latency targets:
  Kaggle T4: < 3 seconds per inference call
  Local CPU:  30-60 seconds (acceptable for local prompt testing only)
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from loguru import logger

from backend.data.surgeries import SurgeryType
from backend.data.models    import ORStateSnapshot
from backend.llm.prompt_builder import PromptBuilder
from backend.llm.output_parser  import parse_llm_output
from backend.llm.schemas        import LLMOutput

# ── model path ────────────────────────────────────────────────────────────────
_MODEL_PATH = (
    Path(__file__).parent.parent.parent
    / "models" / "medgemma" / "medgemma-4b-it-Q3_K_M.gguf"
)

# ── inference defaults ────────────────────────────────────────────────────────
DEFAULT_MAX_TOKENS  = 256    # JSON output is never more than ~200 tokens
DEFAULT_TEMPERATURE = 0.1    # Near-deterministic — we want consistent JSON
DEFAULT_TOP_P       = 0.9
DEFAULT_N_CTX       = 4096   # Context window — system prompt + history fits


class MedGemmaModel:
    """
    Wrapper around llama-cpp-python for MedGemma inference.

    Usage
    -----
    model = MedGemmaModel(surgery=SurgeryType.HEART_TRANSPLANT)
    result: LLMOutput = model.infer(
        transcription = "turn on the patient monitor",
        snapshot      = current_state_snapshot,   # or None for first call
    )
    # result.machine_states["1"] → machines to turn ON
    # result.machine_states["0"] → machines to turn OFF
    """

    def __init__(
        self,
        surgery:       SurgeryType,
        model_path:    Optional[Path]   = None,
        n_gpu_layers:  int              = -1,    # -1 = all layers on GPU
        n_ctx:         int              = DEFAULT_N_CTX,
        n_threads:     int              = 4,
        verbose:       bool             = False,
    ):
        self.surgery   = surgery
        self.model_path = model_path or _MODEL_PATH

        # Lazy import — llama-cpp-python is optional on local dev
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError(
                "llama-cpp-python is not installed.\n"
                "Install with CUDA support for Kaggle:\n"
                '  CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python\n'
                "Or CPU-only:\n"
                "  pip install llama-cpp-python"
            )

        logger.info(f"Loading MedGemma from {self.model_path} ...")
        logger.info(f"  n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx}, n_threads={n_threads}")

        self._llm = Llama(
            model_path   = str(self.model_path),
            n_gpu_layers = n_gpu_layers,
            n_ctx        = n_ctx,
            n_threads    = n_threads,
            verbose      = verbose,
        )

        self._prompt_builder = PromptBuilder(surgery)
        logger.info("MedGemma model loaded.")

    def infer(
        self,
        transcription: str,
        snapshot:      Optional[ORStateSnapshot] = None,
        max_tokens:    int                       = DEFAULT_MAX_TOKENS,
        temperature:   float                     = DEFAULT_TEMPERATURE,
        top_p:         float                     = DEFAULT_TOP_P,
    ) -> LLMOutput:
        """
        Run one inference: transcription + current state → LLMOutput.

        Parameters
        ----------
        transcription : str            MedASR output for this utterance
        snapshot      : ORStateSnapshot | None
                        Current machine states for context
        max_tokens    : int            Max tokens to generate
        temperature   : float          Sampling temperature (0.1 = near-deterministic)
        top_p         : float          Nucleus sampling p

        Returns
        -------
        LLMOutput  Always returns valid object (safe fallback on error)
        """
        messages = self._prompt_builder.build_messages(transcription, snapshot)

        try:
            response = self._llm.create_chat_completion(
                messages    = messages,
                max_tokens  = max_tokens,
                temperature = temperature,
                top_p       = top_p,
                stop        = ["\n\n\n"],   # extra safety stop to prevent rambling
            )
            raw_text = response["choices"][0]["message"]["content"]

        except Exception as exc:
            logger.error(f"MedGemma inference error: {exc}")
            return LLMOutput(reasoning=f"Inference error: {exc}")

        logger.debug(f"MedGemma raw output:\n{raw_text}")

        result = parse_llm_output(raw_text, self.surgery)
        return result

    def change_surgery(self, surgery: SurgeryType) -> None:
        """Switch to a different surgery without reloading the model."""
        self.surgery = surgery
        self._prompt_builder = PromptBuilder(surgery)
        logger.info(f"MedGemma switched to surgery: {surgery}")
