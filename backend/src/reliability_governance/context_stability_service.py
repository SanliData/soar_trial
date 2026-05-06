"""
MODULE: context_stability_service
PURPOSE: Runtime context stability heuristics (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_context_stability(
    *,
    rot_score: float = 0.0,
    context_chars: int = 0,
    summarization_jump_ratio: float = 0.0,
    metadata_inconsistency_ratio: float = 0.0,
) -> dict[str, Any]:
    rot = max(0.0, min(1.0, float(rot_score)))
    cc = max(0, int(context_chars))
    sj = max(0.0, min(1.0, float(summarization_jump_ratio)))
    mi = max(0.0, min(1.0, float(metadata_inconsistency_ratio)))
    size_pressure = min(1.0, cc / 400_000.0)
    stability = round(1.0 - (0.35 * rot + 0.25 * size_pressure + 0.2 * sj + 0.2 * mi), 4)
    recommendations = []
    if rot > 0.55:
        recommendations.append("compress_or_checkpoint_context")
    if size_pressure > 0.7:
        recommendations.append("reduce_context_footprint")
    if sj > 0.35:
        recommendations.append("stabilize_summarization_pipeline")
    if mi > 0.2:
        recommendations.append("align_runtime_metadata_schema")
    return {
        "context_stability_score": max(0.0, stability),
        "recommendations": recommendations,
        "flags": {
            "context_decay": rot > 0.45,
            "oversized_context": size_pressure > 0.65,
            "unstable_summarization": sj > 0.3,
            "metadata_inconsistency": mi > 0.15,
        },
        "heuristic": "stability_blend_v1",
    }
