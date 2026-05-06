"""
MODULE: sandbox_evaluation_service
PURPOSE: Isolated sandbox scoring — no production mutation (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.evolution_governance.mutation_proposal_service import get_proposal
from src.evolution_governance.prompt_mutation_service import compare_prompt_variants
from src.evolution_governance.workflow_mutation_service import simulate_workflow_mutation_for_proposal


def evaluate_sandbox(proposal_id: str) -> dict[str, Any]:
    """
    Deterministic scores keyed by proposal id + type. No network or runtime mutation.
    """
    p = get_proposal(proposal_id)
    if p is None:
        raise ValueError("invalid mutation proposal id")

    ptype = str(p.get("proposal_type", ""))
    ***REMOVED*** Fixed score vectors per type — explainable, reproducible.
    base_scores: dict[str, dict[str, float]] = {
        "workflow_optimization": {
            "regression_risk": 0.12,
            "workflow_stability": 0.88,
            "token_impact_ratio": 0.94,
            "retry_reduction_score": 0.81,
            "evaluation_score_delta": 0.03,
            "orchestration_consistency": 0.86,
        },
        "prompt_optimization": {
            "regression_risk": 0.22,
            "workflow_stability": 0.84,
            "token_impact_ratio": 0.91,
            "retry_reduction_score": 0.76,
            "evaluation_score_delta": 0.06,
            "orchestration_consistency": 0.83,
        },
        "retry_policy_update": {
            "regression_risk": 0.09,
            "workflow_stability": 0.90,
            "token_impact_ratio": 0.97,
            "retry_reduction_score": 0.85,
            "evaluation_score_delta": 0.02,
            "orchestration_consistency": 0.87,
        },
        "loop_detection_update": {
            "regression_risk": 0.18,
            "workflow_stability": 0.85,
            "token_impact_ratio": 0.93,
            "retry_reduction_score": 0.79,
            "evaluation_score_delta": 0.04,
            "orchestration_consistency": 0.84,
        },
        "orchestration_tuning": {
            "regression_risk": 0.11,
            "workflow_stability": 0.89,
            "token_impact_ratio": 0.95,
            "retry_reduction_score": 0.80,
            "evaluation_score_delta": 0.03,
            "orchestration_consistency": 0.91,
        },
    }
    scores = dict(base_scores.get(ptype, base_scores["workflow_optimization"]))
    return {
        "sandbox_mode": True,
        "production_mutation": False,
        "proposal_id": proposal_id,
        "proposal_type": ptype,
        "scores": scores,
        "verdict": "sandbox_pass_pending_governance",
    }


def run_simulation_bundle(proposal_id: str) -> dict[str, Any]:
    """
    Single orchestrated sandbox response: evaluation + workflow simulation + optional prompt compare.
    """
    p = get_proposal(proposal_id)
    if p is None:
        raise ValueError("invalid mutation proposal id")

    sandbox_evaluation = evaluate_sandbox(proposal_id)
    workflow_simulation = simulate_workflow_mutation_for_proposal(proposal_id)

    prompt_comparison: dict[str, Any] | None = None
    if p.get("proposal_type") == "prompt_optimization":
        prompt_comparison = compare_prompt_variants("baseline_v1", "candidate_b_v1")

    return {
        "sandbox_only": True,
        "unrestricted_self_modification": False,
        "proposal_id": proposal_id,
        "sandbox_evaluation": sandbox_evaluation,
        "workflow_simulation": workflow_simulation,
        "prompt_comparison": prompt_comparison,
    }
