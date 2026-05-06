"""
ROUTER: agentic_identity_router
PURPOSE: Agentic identity governance facade (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.agentic_identity.agent_identity_registry import export_identity_registry
from src.agentic_identity.identity_audit_service import export_identity_audit_log
from src.agentic_identity.identity_budget_service import export_identity_budgets
from src.agentic_identity.mcp_endpoint_governance import export_mcp_endpoint_governance
from src.agentic_identity.runtime_access_policy import export_runtime_access_policies
from src.agentic_identity.shadow_agent_detection import export_shadow_agent_detection

router = APIRouter(prefix="/system/identity", tags=["agentic-identity"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "agentic_identity_foundation": True,
        "identity_governed": True,
        "no_hidden_identity_mutation": True,
        "no_self_authorizing_agents": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/registry")
async def get_registry() -> Dict[str, Any]:
    return _envelope(export_identity_registry(limit=50))


@router.get("/policies")
async def get_policies() -> Dict[str, Any]:
    return _envelope(export_runtime_access_policies())


@router.get("/audit")
async def get_audit() -> Dict[str, Any]:
    return _envelope(export_identity_audit_log(identity_id="id-001", limit=50))


@router.get("/budgets")
async def get_budgets() -> Dict[str, Any]:
    return _envelope(export_identity_budgets())


@router.get("/shadow-agents")
async def get_shadow_agents() -> Dict[str, Any]:
    return _envelope(export_shadow_agent_detection())


@router.get("/mcp-governance")
async def get_mcp_governance() -> Dict[str, Any]:
    return _envelope(export_mcp_endpoint_governance())

