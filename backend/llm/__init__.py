"""
backend/llm — Phase 3: MedGemma Integration

Public API
----------
MedGemmaModel   – GGUF inference runner (llama-cpp-python)
PromptBuilder   – Builds system + user messages for create_chat_completion()
parse_llm_output – Robust JSON extractor with 6 fallback strategies
LLMOutput       – Pydantic model validating MedGemma JSON response
"""

from backend.llm.schemas        import LLMOutput
from backend.llm.prompt_builder import PromptBuilder
from backend.llm.output_parser  import parse_llm_output

# MedGemmaModel has a hard dependency on llama-cpp-python which may not be
# installed locally; import lazily so the rest of the package still works.
try:
    from backend.llm.medgemma import MedGemmaModel
except ImportError:
    MedGemmaModel = None  # type: ignore[assignment,misc]

__all__ = [
    "LLMOutput",
    "PromptBuilder",
    "parse_llm_output",
    "MedGemmaModel",
]
