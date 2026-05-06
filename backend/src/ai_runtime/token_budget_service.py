"""
MODULE: token_budget_service
PURPOSE: Deterministic token approximation and budget enforcement (H-021)
ENCODING: UTF-8 WITHOUT BOM
"""

from src.ai_runtime.runtime_schema import TokenBudgetResult


def estimate_tokens(text: str) -> int:
    """Rough deterministic tokenizer surrogate (no external deps)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def enforce_token_budget(text: str, max_tokens: int) -> TokenBudgetResult:
    """
    Enforce an upper bound by truncating UTF-8 safe substring bound to char budget.
    Never raises for oversized text; invalid max_tokens raises ValueError.
    """
    if max_tokens < 1:
        raise ValueError("max_tokens must be >= 1")
    est = estimate_tokens(text)
    if est <= max_tokens:
        return TokenBudgetResult(text=text, truncated=False, warning=None)

    max_chars = max_tokens * 4
    truncated = text[:max_chars]
    warning = "Input truncated deterministically to satisfy max_input_tokens."
    return TokenBudgetResult(text=truncated, truncated=True, warning=warning)
