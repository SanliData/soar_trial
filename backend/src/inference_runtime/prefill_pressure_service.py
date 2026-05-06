"""
MODULE: prefill_pressure_service
PURPOSE: Prefill pressure classification — governance metadata (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.long_context_runtime.context_pressure_service import classify_prefill_amplification

_LEVELS = ("low", "moderate", "high", "critical")


def classify_prefill_pressure(metrics: dict[str, Any]) -> dict[str, Any]:
    """
    Levels: low, moderate, high, critical — no automatic optimization applied.
    """
    ctx_tokens = int(metrics.get("context_tokens") or 0)
    prefill_repeat = int(metrics.get("prefill_repeat_count") or 0)
    duplicates = int(metrics.get("duplicate_context_chunks") or 0)
    retrieval_breadth = int(metrics.get("retrieval_documents") or 0)
    inefficient_skill_prefill = int(metrics.get("inefficient_skill_prefill_signals") or 0)

    score = 0
    if ctx_tokens > 32000:
        score += 2
    elif ctx_tokens > 16000:
        score += 1
    if prefill_repeat > 4:
        score += 2
    elif prefill_repeat > 2:
        score += 1
    if duplicates > 6:
        score += 2
    elif duplicates > 2:
        score += 1
    if retrieval_breadth > 24:
        score += 2
    elif retrieval_breadth > 12:
        score += 1
    if inefficient_skill_prefill > 2:
        score += 1

    if score >= 6:
        level = "critical"
    elif score >= 4:
        level = "high"
    elif score >= 2:
        level = "moderate"
    else:
        level = "low"

    return {
        "pressure_level": level,
        "score": score,
        "allowed_levels": list(_LEVELS),
        "automatic_runtime_optimization": False,
        "deterministic": True,
    }


def export_prefill_pressure_manifest() -> dict[str, Any]:
    return {
        "classification_examples": [
            classify_prefill_pressure(
                {"context_tokens": 8000, "prefill_repeat_count": 1, "duplicate_context_chunks": 0, "retrieval_documents": 4}
            ),
            classify_prefill_pressure(
                {
                    "context_tokens": 48000,
                    "prefill_repeat_count": 6,
                    "duplicate_context_chunks": 10,
                    "retrieval_documents": 28,
                    "inefficient_skill_prefill_signals": 4,
                }
            ),
        ],
        "prefill_amplification_governance": [
            classify_prefill_amplification({"prefill_repeat_count": 1, "decoded_token_growth_ratio": 1.1}),
            classify_prefill_amplification({"prefill_repeat_count": 9, "decoded_token_growth_ratio": 3.0}),
        ],
        "h043_prefill_amplification_detection": True,
        "deterministic": True,
    }
