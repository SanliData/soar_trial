"""
ROUTER: mcp_runtime_router
PURPOSE: HTTP facade for MCP runtime compatibility projections (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.mcp_runtime.mcp_agent_gateway import export_mcp_gateway_manifest
from src.mcp_runtime.mcp_capability_registry import export_mcp_capability_registry
from src.mcp_runtime.mcp_tool_projection_service import project_mcp_tools
from src.mcp_runtime.mcp_transport_service import export_mcp_transport_manifest

router = APIRouter(tags=["mcp-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "mcp_runtime_compatibility_foundation": True,
        "public_mcp_server_required_now": False,
        "unrestricted_mcp_execution": False,
        "external_execution_enabled": False,
        "policy_scoped_tools_only": True,
    }
    merged.update(payload)
    return merged


@router.get("/system/mcp/capabilities")
async def get_mcp_capabilities() -> Dict[str, Any]:
    return _envelope({"mcp_capabilities": export_mcp_capability_registry(policy_scope="internal_operator")})


@router.get("/system/mcp/tools")
async def get_mcp_tools() -> Dict[str, Any]:
    return _envelope({"mcp_tools": project_mcp_tools(policy_scope="internal_operator")})


@router.get("/system/mcp/transports")
async def get_mcp_transports() -> Dict[str, Any]:
    return _envelope({"mcp_transports": export_mcp_transport_manifest()})


@router.get("/system/mcp/gateway")
async def get_mcp_gateway() -> Dict[str, Any]:
    return _envelope({"mcp_gateway": export_mcp_gateway_manifest()})

