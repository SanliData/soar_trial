"""
ROUTER: system_visibility_router
PURPOSE: Unified operational admin & system visibility API (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.system_visibility.active_agent_visibility_service import export_active_agent_visibility
from src.system_visibility.approval_queue_service import export_approval_queue
from src.system_visibility.connector_freshness_service import export_connector_freshness
from src.system_visibility.orchestration_trace_service import export_orchestration_trace
from src.system_visibility.retrieval_visibility_service import export_retrieval_visibility
from src.system_visibility.runtime_pressure_service import export_runtime_pressure
from src.system_visibility.system_health_service import export_system_health
from src.system_visibility.workflow_audit_service import export_workflow_audit

router = APIRouter(tags=["system-visibility"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "system_visibility_foundation": True,
        "hidden_admin_backdoor": False,
        "unrestricted_internal_controls": False,
        "deterministic": True,
    }
    merged.update(payload)
    return merged


@router.get("/system/visibility/health")
async def get_system_health() -> Dict[str, Any]:
    return _envelope({"health": export_system_health()})


@router.get("/system/visibility/runtime-pressure")
async def get_runtime_pressure() -> Dict[str, Any]:
    return _envelope({"runtime_pressure": export_runtime_pressure()})


@router.get("/system/visibility/workflow-audit")
async def get_workflow_audit() -> Dict[str, Any]:
    return _envelope({"workflow_audit": export_workflow_audit(workflow_scope="procurement_analysis")})


@router.get("/system/visibility/retrieval")
async def get_retrieval_visibility() -> Dict[str, Any]:
    return _envelope({"retrieval": export_retrieval_visibility()})


@router.get("/system/visibility/connectors")
async def get_connector_visibility() -> Dict[str, Any]:
    return _envelope({"connectors": export_connector_freshness()})


@router.get("/system/visibility/orchestration")
async def get_orchestration_visibility() -> Dict[str, Any]:
    return _envelope({"orchestration": export_orchestration_trace()})


@router.get("/system/visibility/approvals")
async def get_approval_queue() -> Dict[str, Any]:
    return _envelope({"approvals": export_approval_queue()})


@router.get("/system/visibility/agents")
async def get_agent_visibility() -> Dict[str, Any]:
    return _envelope({"agents": export_active_agent_visibility()})

