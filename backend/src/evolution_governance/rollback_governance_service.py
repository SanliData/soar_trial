"""
MODULE: rollback_governance_service
PURPOSE: Rollback readiness — governance-gated, auditable (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.evolution_governance.mutation_proposal_service import get_proposal


def assess_rollback_readiness(
    proposal_id: str,
    *,
    mutation_deployed: bool,
    governance_approval_completed: bool,
    evaluation_trace_stored: bool,
) -> dict[str, Any]:
    p = get_proposal(proposal_id)
    if p is None:
        raise ValueError("invalid mutation proposal id")

    rollback_available = bool(p.get("rollback_available"))
    rollback_path_exists = rollback_available and not mutation_deployed
    mutation_reversible = rollback_available
    checks = {
        "rollback_path_exists": rollback_path_exists,
        "mutation_reversible": mutation_reversible,
        "evaluation_traces_stored": evaluation_trace_stored,
        "governance_approval_completed": governance_approval_completed,
    }
    all_ready = (
        rollback_path_exists
        and mutation_reversible
        and evaluation_trace_stored
        and governance_approval_completed
        and rollback_available
    )
    return {
        "proposal_id": proposal_id,
        "rollback_mandatory_for_deploy": True,
        "rollback_ready": bool(all_ready),
        "checks": checks,
        "immutable_trace_preferred": True,
    }
