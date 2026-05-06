"""
MODULE: prompt_compaction_service
PURPOSE: Deterministic head/tail compaction without LLM calls (H-021)
ENCODING: UTF-8 WITHOUT BOM
"""

from src.ai_runtime.runtime_schema import CompactionResult
from src.ai_runtime.token_budget_service import estimate_tokens

_MARKER = "\n\n[Context compacted deterministically]\n\n"


def compact_context(text: str, max_tokens: int) -> CompactionResult:
    """
    Preserve beginning and end of long text; insert deterministic marker when compaction triggers.
    """
    orig = estimate_tokens(text)
    if max_tokens < 1:
        raise ValueError("max_tokens must be >= 1")
    if orig <= max_tokens:
        return CompactionResult(
            compacted_text=text,
            original_estimated_tokens=orig,
            compacted_estimated_tokens=orig,
            compaction_applied=False,
        )

    budget_chars = max(1, max_tokens * 4 - len(_MARKER))
    half = budget_chars // 2
    head = text[:half]
    tail = text[-half:] if half > 0 else ""
    compacted = head + _MARKER + tail
    compacted_est = estimate_tokens(compacted)
    return CompactionResult(
        compacted_text=compacted,
        original_estimated_tokens=orig,
        compacted_estimated_tokens=max(1, compacted_est),
        compaction_applied=True,
    )
