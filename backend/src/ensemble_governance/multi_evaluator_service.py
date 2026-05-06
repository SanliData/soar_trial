"""
MODULE: multi_evaluator_service
PURPOSE: Ensemble evaluators — deterministic orchestration, weights explicit (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_EVALUATORS: list[dict[str, Any]] = [
    {"evaluator_id": "ev-policy", "weight": 0.34, "profile": "policy_lint"},
    {"evaluator_id": "ev-structure", "weight": 0.33, "profile": "schema_adherence"},
    {"evaluator_id": "ev-safety", "weight": 0.33, "profile": "risk_flags"},
]


def export_multi_evaluator_manifest() -> dict[str, Any]:
    wsum = sum(float(e["weight"]) for e in _EVALUATORS)
    return {
        "evaluators": [dict(e) for e in _EVALUATORS],
        "weight_sum": round(wsum, 4),
        "weighting_public": True,
        "hidden_evaluator_weighting": False,
        "evaluator_diversity_metadata": {"distinct_profiles": len({e["profile"] for e in _EVALUATORS})},
        "deterministic_orchestration": True,
        "deterministic": True,
    }
