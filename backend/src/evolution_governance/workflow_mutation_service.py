"""
MODULE: workflow_mutation_service
PURPOSE: Sandbox workflow mutation simulation only — no production changes (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.evolution_governance.mutation_proposal_service import get_proposal


def simulate_workflow_mutation(scenario: str) -> dict[str, Any]:
    """
    Named scenarios produce deterministic pseudo-deltas for lab review.
    """
    key = scenario.strip().lower()
    scenarios: dict[str, dict[str, Any]] = {
        "retry_reduction": {
            "retry_reduction_delta": -0.15,
            "loop_detection_sensitivity": 0.0,
            "subagent_limit_delta": 0,
            "context_compression_ratio": 1.0,
        },
        "loop_detection": {
            "retry_reduction_delta": 0.0,
            "loop_detection_sensitivity": 0.12,
            "subagent_limit_delta": 0,
            "context_compression_ratio": 1.0,
        },
        "subagent_limits": {
            "retry_reduction_delta": 0.0,
            "loop_detection_sensitivity": 0.0,
            "subagent_limit_delta": -1,
            "context_compression_ratio": 1.0,
        },
        "context_compression": {
            "retry_reduction_delta": 0.0,
            "loop_detection_sensitivity": 0.0,
            "subagent_limit_delta": 0,
            "context_compression_ratio": 0.92,
        },
    }
    if key not in scenarios:
        raise ValueError("unknown workflow mutation scenario")
    payload = dict(scenarios[key])
    payload.update(
        {
            "simulation_only": True,
            "production_mutation": False,
            "scenario": key,
        }
    )
    return payload


def simulate_workflow_mutation_for_proposal(proposal_id: str) -> dict[str, Any]:
    p = get_proposal(proposal_id)
    if p is None:
        raise ValueError("invalid mutation proposal id")
    ptype = str(p.get("proposal_type", ""))
    scenario_map = {
        "workflow_optimization": "retry_reduction",
        "prompt_optimization": "context_compression",
        "retry_policy_update": "retry_reduction",
        "loop_detection_update": "loop_detection",
        "orchestration_tuning": "subagent_limits",
    }
    scenario = scenario_map.get(ptype, "retry_reduction")
    base = simulate_workflow_mutation(scenario)
    base["proposal_id"] = proposal_id
    base["proposal_type"] = ptype
    return base
