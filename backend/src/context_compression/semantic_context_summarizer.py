"""
MODULE: semantic_context_summarizer
PURPOSE: Deterministic semantic context summarization (no LLM calls) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import math
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item

_MARKER = "[Context compressed deterministically]"


def _estimate_tokens(text: str) -> int:
    return max(0, int(len(text or "") / 4))


def _truncate_preserve_ends(text: str, *, max_chars: int) -> tuple[str, bool]:
    s = text or ""
    if len(s) <= max_chars:
        return s, False
    head = max(0, max_chars // 2 - 60)
    tail = max(0, max_chars // 2 - 60)
    out = s[:head].rstrip() + "\n...[TRUNCATED]...\n" + s[-tail:].lstrip()
    return out, True


def summarize_context(
    item: dict[str, Any],
    *,
    max_tokens: int = 800,
    allow_guardrail_compression: bool = False,
) -> dict[str, Any]:
    validate_context_item(item)
    ct = str(item["context_type"]).strip()
    original = str(item.get("content_summary") or "")
    original_tokens = int(item.get("token_estimate") or _estimate_tokens(original))

    if ct == "guardrail_context" and not allow_guardrail_compression:
        return {
            "context_id": item["context_id"],
            "context_type": ct,
            "preserved": True,
            "summary": original,
            "original_token_estimate": original_tokens,
            "compressed_token_estimate": original_tokens,
            "compression_ratio": 1.0,
            "semantic_drift_risk": "none",
            "marker": None,
        }

    ***REMOVED*** deterministic char budget from token budget
    max_chars = max(120, int(max_tokens * 4))
    truncated, was_truncated = _truncate_preserve_ends(original, max_chars=max_chars)
    out_text = truncated
    if was_truncated:
        out_text = f"{_MARKER}\n{truncated}"

    compressed_tokens = _estimate_tokens(out_text)
    ratio = 1.0
    if original_tokens > 0:
        ratio = round(compressed_tokens / float(original_tokens), 4)

    drift = "low"
    if was_truncated and ratio < 0.55:
        drift = "medium"
    if was_truncated and ratio < 0.35:
        drift = "high"

    return {
        "context_id": item["context_id"],
        "context_type": ct,
        "preserved": False,
        "summary": out_text,
        "original_token_estimate": original_tokens,
        "compressed_token_estimate": compressed_tokens,
        "compression_ratio": ratio,
        "semantic_drift_risk": drift,
        "marker": _MARKER if was_truncated else None,
    }


def summarize_context_collection(
    items: list[dict[str, Any]],
    *,
    max_tokens_total: int = 8000,
    allow_guardrail_compression: bool = False,
) -> dict[str, Any]:
    """
    Deterministic multi-item summarization with per-type budget slicing.
    Guardrails remain visible separately unless explicitly allowed.
    """
    if max_tokens_total < 400:
        max_tokens_total = 400

    validated = [dict(x) for x in items]
    for it in validated:
        validate_context_item(it)

    ***REMOVED*** Deterministic per-type weight allocations (sum to 1.0)
    weights: dict[str, float] = {
        "guardrail_context": 0.22,
        "instruction_context": 0.18,
        "tool_context": 0.18,
        "knowledge_context": 0.16,
        "memory_context": 0.14,
        "example_context": 0.12,
    }
    ***REMOVED*** Ensure stable order
    validated.sort(key=lambda x: (x["workflow_scope"], x["context_type"], x["context_id"]))

    summaries: list[dict[str, Any]] = []
    for it in validated:
        ct = str(it["context_type"]).strip()
        w = float(weights.get(ct, 0.1))
        per_item_tokens = max(120, int(math.floor(max_tokens_total * w / max(1, len(validated)))))
        summaries.append(
            summarize_context(
                it,
                max_tokens=per_item_tokens,
                allow_guardrail_compression=allow_guardrail_compression,
            )
        )

    original_total = sum(int(s["original_token_estimate"]) for s in summaries)
    compressed_total = sum(int(s["compressed_token_estimate"]) for s in summaries)
    ratio = 1.0 if original_total <= 0 else round(compressed_total / float(original_total), 4)

    drift_risk = "low"
    if any(s["semantic_drift_risk"] == "high" for s in summaries):
        drift_risk = "high"
    elif any(s["semantic_drift_risk"] == "medium" for s in summaries):
        drift_risk = "medium"

    return {
        "summaries": summaries,
        "original_token_estimate": original_total,
        "compressed_token_estimate": compressed_total,
        "compression_ratio": ratio,
        "semantic_drift_risk": drift_risk,
        "deterministic": True,
        "llm_invoked": False,
    }

