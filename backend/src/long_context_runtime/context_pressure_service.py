"""
MODULE: context_pressure_service
PURPOSE: Long-context operational pressure — deterministic, no auto mutation (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def classify_context_pressure(metrics: dict[str, Any]) -> dict[str, Any]:
    oversized = int(metrics.get("context_window_tokens") or 0)
    breadth = int(metrics.get("retrieval_doc_breadth") or 0)
    dup = int(metrics.get("duplicated_blocks") or 0)
    refl = float(metrics.get("reflection_share") or 0.0)
    depth = int(metrics.get("orchestration_depth_hint") or 0)

    score = 0
    if oversized > 64000:
        score += 3
    elif oversized > 32000:
        score += 2
    elif oversized > 16000:
        score += 1
    if breadth > 32:
        score += 2
    elif breadth > 16:
        score += 1
    if dup > 12:
        score += 2
    elif dup > 4:
        score += 1
    if refl > 0.35:
        score += 2
    elif refl > 0.2:
        score += 1
    if depth > 10:
        score += 2
    elif depth > 6:
        score += 1

    if score >= 8:
        level = "critical"
    elif score >= 5:
        level = "high"
    elif score >= 2:
        level = "moderate"
    else:
        level = "low"

    return {
        "pressure_level": level,
        "score": score,
        "checks_considered": [
            "oversized_context_windows",
            "excessive_retrieval_breadth",
            "duplicated_context_blocks",
            "reflection_overload",
            "orchestration_depth_inflation",
        ],
        "autonomous_context_mutation": False,
        "deterministic": True,
    }


def classify_prefill_amplification(metrics: dict[str, Any]) -> dict[str, Any]:
    """Amplification when repeated prefill inflates decoder-bound work without new information."""
    repeat = int(metrics.get("prefill_repeat_count") or 0)
    growth = float(metrics.get("decoded_token_growth_ratio") or 1.0)
    score = 0
    if repeat > 6:
        score += 3
    elif repeat > 3:
        score += 1
    if growth > 2.5:
        score += 2
    elif growth > 1.8:
        score += 1
    tier = "nominal"
    if score >= 5:
        tier = "elevated_risk"
    elif score >= 2:
        tier = "watch"
    return {"prefill_amplification_tier": tier, "score": score, "deterministic": True}


def export_context_pressure_manifest() -> dict[str, Any]:
    return {
        "examples": [
            classify_context_pressure(
                {
                    "context_window_tokens": 12000,
                    "retrieval_doc_breadth": 6,
                    "duplicated_blocks": 1,
                    "reflection_share": 0.1,
                    "orchestration_depth_hint": 3,
                }
            ),
            classify_context_pressure(
                {
                    "context_window_tokens": 72000,
                    "retrieval_doc_breadth": 40,
                    "duplicated_blocks": 15,
                    "reflection_share": 0.4,
                    "orchestration_depth_hint": 12,
                }
            ),
        ],
        "prefill_amplification_examples": [
            classify_prefill_amplification({"prefill_repeat_count": 2, "decoded_token_growth_ratio": 1.2}),
            classify_prefill_amplification({"prefill_repeat_count": 8, "decoded_token_growth_ratio": 2.8}),
        ],
        "deterministic": True,
    }
