"""
MODULE: active_agent_visibility_service
PURPOSE: Active/idle/restricted/high-risk/approval-blocked agent visibility (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import export_agent_registry
from src.system_visibility.approval_queue_service import export_approval_queue


def export_active_agent_visibility() -> dict[str, Any]:
    reg = export_agent_registry()["agents"]
    approvals = export_approval_queue()
    pending = approvals.get("pending_approvals") or []

    active = [a for a in reg if a.get("status") == "active"]
    idle = [a for a in reg if a.get("status") == "paused"]
    restricted = [a for a in reg if a.get("permission_scope") != "governed_readonly"]
    high_risk = [a for a in reg if a.get("human_approval_required") is True]

    blocked_agent_ids = {str(a.get("target_agent_type") or "") for a in pending if a.get("target_agent_type")}
    approval_blocked = [a for a in reg if a.get("agent_id") in blocked_agent_ids] if blocked_agent_ids else []

    return {
        "active_agents": [a["agent_id"] for a in active],
        "idle_agents": [a["agent_id"] for a in idle],
        "restricted_agents": [a["agent_id"] for a in restricted],
        "high_risk_agents": [a["agent_id"] for a in high_risk],
        "approval_blocked_agents": [a["agent_id"] for a in approval_blocked],
        "observability_only": True,
        "no_autonomous_intervention": True,
        "deterministic": True,
    }

