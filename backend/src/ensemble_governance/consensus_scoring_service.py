"""
MODULE: consensus_scoring_service
PURPOSE: Consensus aggregation — explainable deterministic (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def compute_consensus_scores(scores: tuple[float, ...]) -> dict[str, Any]:
    """scores in [0,1], simple mean + variance."""
    if not scores:
        raise ValueError("empty scores")
    for s in scores:
        if s < 0 or s > 1:
            raise ValueError("scores must be in [0,1]")
    n = len(scores)
    mean = round(sum(scores) / n, 4)
    if n == 1:
        var = 0.0
    else:
        var = round(sum((x - mean) ** 2 for x in scores) / n, 6)
    disagreement_risk = min(1.0, var * 4.0)
    confidence = round(max(0.0, 1.0 - disagreement_risk), 4)
    return {
        "consensus_score": mean,
        "evaluator_variance": var,
        "confidence_score": confidence,
        "disagreement_risk": round(disagreement_risk, 4),
        "aggregation": "plain_mean_with_variance",
        "deterministic": True,
    }


def export_consensus_scoring_manifest() -> dict[str, Any]:
    return {
        "example": compute_consensus_scores((0.82, 0.79, 0.85)),
        "deterministic": True,
    }
