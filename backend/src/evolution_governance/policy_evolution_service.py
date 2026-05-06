"""
MODULE: policy_evolution_service
PURPOSE: Governance-gated orchestration policy proposals — deterministic only (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

GOVERNANCE_EPOCH = "2025-05-01T00:00:00Z"

POLICY_EVOLUTION_SLOTS: list[dict[str, Any]] = [
    {
        "policy_slot_id": "delegation-limits-v1",
        "domain": "orchestration",
        "current": "max_delegation_depth=2",
        "candidate": "max_delegation_depth=2; stall_after_transitions=3",
        "governance_approval_required": True,
        "autonomous_deploy": False,
        "created_at": GOVERNANCE_EPOCH,
    },
    {
        "policy_slot_id": "retry-policies-v1",
        "domain": "reliability",
        "current": "exponential_backoff_base=2",
        "candidate": "cap_multiplier_at=2.5",
        "governance_approval_required": True,
        "autonomous_deploy": False,
        "created_at": GOVERNANCE_EPOCH,
    },
    {
        "policy_slot_id": "escalation-v1",
        "domain": "workflow",
        "current": "escalate_on_acceptance_failure=true",
        "candidate": "add_human_checkpoint_on_second_failure=true",
        "governance_approval_required": True,
        "autonomous_deploy": False,
        "created_at": GOVERNANCE_EPOCH,
    },
    {
        "policy_slot_id": "context-reset-v1",
        "domain": "runtime_context",
        "current": "reset_on_token_pressure=0.92",
        "candidate": "reset_on_token_pressure=0.90; preserve_evidence_handles=true",
        "governance_approval_required": True,
        "autonomous_deploy": False,
        "created_at": GOVERNANCE_EPOCH,
    },
]


def export_policy_evolution_manifest() -> dict[str, Any]:
    return {
        "policies": list(POLICY_EVOLUTION_SLOTS),
        "proposal_only": True,
        "governance_gated": True,
        "slot_count": len(POLICY_EVOLUTION_SLOTS),
    }
