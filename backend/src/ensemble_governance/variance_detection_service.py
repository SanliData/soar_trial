"""
MODULE: variance_detection_service
PURPOSE: Evaluator disagreement governance — no suppression (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def detect_evaluator_variance_issues(*, variance: float, rank_entropy: float, score_spread: float) -> dict[str, Any]:
    flags: list[str] = []
    if variance > 0.08:
        flags.append("high_evaluator_variance")
    if rank_entropy > 0.92:
        flags.append("inconsistent_workflow_scoring")
    if score_spread > 0.45:
        flags.append("unstable_ranking_patterns")
    if len(flags) >= 2:
        flags.append("unreliable_operational_output_risk")
    return {
        "flags": sorted(set(flags)),
        "thresholds": {"variance": 0.08, "rank_entropy": 0.92, "score_spread": 0.45},
        "hidden_variance_suppression": False,
        "deterministic_thresholds": True,
        "deterministic": True,
    }


def export_variance_detection_manifest() -> dict[str, Any]:
    return {
        "examples": [
            detect_evaluator_variance_issues(variance=0.02, rank_entropy=0.4, score_spread=0.15),
            detect_evaluator_variance_issues(variance=0.11, rank_entropy=0.95, score_spread=0.52),
        ],
        "deterministic": True,
    }
