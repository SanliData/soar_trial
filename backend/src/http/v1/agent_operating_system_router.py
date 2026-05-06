"""
ROUTER: agent_operating_system_router
PURPOSE: HTTP facade for agent operating system (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.agent_operating_system.agent_fleet_service import export_agent_fleet_status
from src.agent_operating_system.agent_observability_service import export_agent_observability_manifest
from src.agent_operating_system.agent_permission_governance import evaluate_agent_permission_gate
from src.agent_operating_system.agent_registry_service import export_agent_registry
from src.agent_operating_system.agent_role_service import export_agent_roles

router = APIRouter(tags=["agent-operating-system"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "agent_operating_system_foundation": True,
        "autonomous_agent_swarms": False,
        "autonomous_fleet_mutation": False,
        "hidden_execution_permissions": False,
        "unrestricted_nl_execution": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/agents")
async def get_agents() -> Dict[str, Any]:
    return _envelope({"registry": export_agent_registry()})


@router.get("/system/agents/roles")
async def get_agent_roles() -> Dict[str, Any]:
    return _envelope({"roles": export_agent_roles()})


@router.get("/system/agents/fleet")
async def get_agent_fleet() -> Dict[str, Any]:
    return _envelope({"fleet": export_agent_fleet_status()})


@router.get("/system/agents/permissions")
async def get_agent_permissions() -> Dict[str, Any]:
    # deterministic sample gate evaluation (no real principal context)
    sample = evaluate_agent_permission_gate(
        agent_id="procurement_agent",
        requested_capability_id="context.types",
        workflow_scope="procurement_analysis",
        high_risk_command=True,
        human_approval_present=False,
    )
    return _envelope({"permission_gate_sample": sample, "fail_closed": True})


@router.get("/system/agents/observability")
async def get_agent_observability() -> Dict[str, Any]:
    return _envelope({"observability": export_agent_observability_manifest()})

