"""
MODULE: review_governance_service
PURPOSE: Deterministic review / gate metadata — auditable (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_review_status() -> dict[str, Any]:
    """Foundation snapshot — operators replace with live CI integration later."""
    return {
        "gates": {
            "verification_completed": {"state": "required", "source": "verify_scripts"},
            "architecture_contracts": {"state": "required", "source": "architecture_contract_service"},
            "security_review": {"state": "required_for_sensitive_changes", "source": "policy"},
            "workflow_evaluation": {"state": "required_for_agent_paths", "source": "trajectory_eval_hooks"},
        },
        "approval_model": "human_in_loop_for_merge",
        "recursive_governance_loop": False,
        "audit_trail_required": True,
        "rule": "static_gate_manifest_v1",
    }
