"""
MODULE: agent_state_projection
PURPOSE: Observability-only agent state projections for event streaming (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import export_agent_registry


def export_agent_states() -> dict[str, Any]:
    agents = export_agent_registry()["agents"]
    projections = []
    for a in agents:
        status = a.get("status") or "unknown"
        waiting = status == "paused"
        approval_blocked = bool(a.get("human_approval_required"))
        projections.append(
            {
                "agent_id": a["agent_id"],
                "active_state": status == "active",
                "waiting_state": waiting,
                "approval_blocked_state": approval_blocked,
                "retrieval_running_state": False,
                "escalation_required_state": approval_blocked,
                "observability_only": True,
                "deterministic": True,
            }
        )
    projections.sort(key=lambda x: x["agent_id"])
    return {"agents": projections, "deterministic": True}

