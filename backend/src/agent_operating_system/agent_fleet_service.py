"""
MODULE: agent_fleet_service
PURPOSE: Fleet visibility and governance warnings (observability only) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import export_agent_registry


def export_agent_fleet_status() -> dict[str, Any]:
    reg = export_agent_registry()
    agents = reg["agents"]
    total = len(agents)
    active = sum(1 for a in agents if a.get("status") == "active")
    paused = sum(1 for a in agents if a.get("status") == "paused")
    high_risk = sum(1 for a in agents if a.get("human_approval_required") is True)
    workflows = sorted({str(a.get("workflow_scope") or "") for a in agents if a.get("workflow_scope")})
    warnings = []
    if paused:
        warnings.append("paused_agents_present")
    if high_risk == 0:
        warnings.append("no_human_approval_agents_flagged_unexpected")
    return {
        "total_agents": total,
        "active_agents": active,
        "paused_agents": paused,
        "high_risk_agents": high_risk,
        "workflows_covered": workflows,
        "governance_warnings": warnings,
        "autonomous_fleet_mutation": False,
        "deterministic": True,
    }

