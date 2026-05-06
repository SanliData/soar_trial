"""
MODULE: mutation_proposal_service
PURPOSE: Controlled optimization proposals — proposal-only, no deployment (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

GOVERNANCE_EPOCH = "2025-05-01T00:00:00Z"

***REMOVED*** Static registry — no runtime mutation API.
MUTATION_PROPOSALS: dict[str, dict[str, Any]] = {
    "mut-wf-opt-001": {
        "proposal_id": "mut-wf-opt-001",
        "proposal_type": "workflow_optimization",
        "target_system": "workflow_governance",
        "proposed_change": "Reduce parallel fan-out cap from 4 to 3 on retry-heavy paths.",
        "expected_benefit": "Lower tail latency variance on unstable delegations.",
        "estimated_risk": "low",
        "rollback_available": True,
        "evaluation_required": True,
        "created_at": GOVERNANCE_EPOCH,
    },
    "mut-prompt-001": {
        "proposal_id": "mut-prompt-001",
        "proposal_type": "prompt_optimization",
        "target_system": "prompt_orchestration",
        "proposed_change": "Add explicit citation clause to planner system prompt variant B.",
        "expected_benefit": "Fewer uncited numerics in intermediate plans.",
        "estimated_risk": "medium",
        "rollback_available": True,
        "evaluation_required": True,
        "created_at": GOVERNANCE_EPOCH,
    },
    "mut-retry-001": {
        "proposal_id": "mut-retry-001",
        "proposal_type": "retry_policy_update",
        "target_system": "reliability_governance",
        "proposed_change": "Cap exponential backoff multiplier at 2.5 for graph retrieval.",
        "expected_benefit": "Reduced token burn on flaky retrieval without full abort.",
        "estimated_risk": "low",
        "rollback_available": True,
        "evaluation_required": True,
        "created_at": GOVERNANCE_EPOCH,
    },
    "mut-loop-001": {
        "proposal_id": "mut-loop-001",
        "proposal_type": "loop_detection_update",
        "target_system": "workflow_governance",
        "proposed_change": "Tighten delegation-depth stall detector window to 3 transitions.",
        "expected_benefit": "Earlier halt on delegation oscillation patterns.",
        "estimated_risk": "medium",
        "rollback_available": True,
        "evaluation_required": True,
        "created_at": GOVERNANCE_EPOCH,
    },
    "mut-orch-001": {
        "proposal_id": "mut-orch-001",
        "proposal_type": "orchestration_tuning",
        "target_system": "semantic_capabilities",
        "proposed_change": "Prefer orchestration_safe=true edges when multiple capability paths tie.",
        "expected_benefit": "More predictable planner picks under ambiguity.",
        "estimated_risk": "low",
        "rollback_available": True,
        "evaluation_required": True,
        "created_at": GOVERNANCE_EPOCH,
    },
}


def export_mutation_proposals_manifest() -> list[dict[str, Any]]:
    return [dict(MUTATION_PROPOSALS[k]) for k in sorted(MUTATION_PROPOSALS.keys())]


def get_proposal(proposal_id: str) -> dict[str, Any] | None:
    key = proposal_id.strip()
    if key not in MUTATION_PROPOSALS:
        return None
    return dict(MUTATION_PROPOSALS[key])
