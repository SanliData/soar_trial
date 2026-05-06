"""
MODULE: agent_permission_governance
PURPOSE: Deterministic permission gates (fail closed) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import get_agent
from src.agent_operating_system.agent_role_service import get_role


def evaluate_agent_permission_gate(
    *,
    agent_id: str,
    requested_capability_id: str,
    workflow_scope: str,
    high_risk_command: bool,
    human_approval_present: bool,
) -> dict[str, Any]:
    """
    Fail-closed deterministic gate:
    - agent must exist
    - workflow scope must match
    - requested capability must be allowed by role and agent record
    - high-risk commands require human approval
    """
    agent = get_agent(agent_id)
    role = get_role(agent["agent_role"])

    wf = (workflow_scope or "").strip()
    if wf != agent["workflow_scope"]:
        return {"allowed": False, "reason": "workflow_scope_mismatch", "deterministic": True}

    cap = (requested_capability_id or "").strip()
    if cap not in set(agent["allowed_capabilities"]):
        return {"allowed": False, "reason": "capability_not_allowed_for_agent", "deterministic": True}
    if cap not in set(role["allowed_capabilities"]):
        return {"allowed": False, "reason": "capability_not_allowed_for_role", "deterministic": True}

    if bool(high_risk_command) and not bool(human_approval_present):
        return {"allowed": False, "reason": "human_approval_required", "deterministic": True}

    return {"allowed": True, "reason": "governed_allow", "deterministic": True}

