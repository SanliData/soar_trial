"""
MODULE: mcp_agent_gateway
PURPOSE: MCP agent gateway metadata (safe, no unrestricted execution) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.capability_gateway.mcp_gateway_registry import export_gateways_manifest
from src.agentic_identity.mcp_endpoint_governance import export_mcp_endpoint_governance


def export_mcp_gateway_manifest() -> dict[str, Any]:
    return {
        "gateway_mode": "projection_only",
        "gateways": export_gateways_manifest(),
        ***REMOVED*** H-049: endpoint governance metadata (no execution)
        "endpoint_governance": export_mcp_endpoint_governance(),
        "policy_scoped_tools_only": True,
        "unrestricted_mcp_execution": False,
        "public_mcp_server": False,
        "deterministic": True,
    }

