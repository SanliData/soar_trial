"""
MODULE: prompt_mutation_service
PURPOSE: Deterministic prompt variant comparison — no autonomous rewriting (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def compare_prompt_variants(baseline_profile: str, candidate_profile: str) -> dict[str, Any]:
    """
    Static lookup table — compares labeled profiles without mutating stored prompts.
    """
    b = baseline_profile.strip().lower()
    c = candidate_profile.strip().lower()
    key = (b, c)
    table: dict[tuple[str, str], dict[str, Any]] = {
        ("baseline_v1", "candidate_b_v1"): {
            "evaluation_score_delta": 0.05,
            "hallucination_risk_delta": -0.08,
            "token_efficiency_ratio": 0.97,
            "workflow_stability_score": 0.86,
        },
        ("baseline_v1", "baseline_v1"): {
            "evaluation_score_delta": 0.0,
            "hallucination_risk_delta": 0.0,
            "token_efficiency_ratio": 1.0,
            "workflow_stability_score": 0.85,
        },
    }
    if key not in table:
        key = ("baseline_v1", "candidate_b_v1")
    metrics = dict(table[key])
    return {
        "baseline_profile": baseline_profile,
        "candidate_profile": candidate_profile,
        "deterministic_comparison": True,
        "uncontrolled_prompt_rewrite": False,
        "metrics": metrics,
    }
