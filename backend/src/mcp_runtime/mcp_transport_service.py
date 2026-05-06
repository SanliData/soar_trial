"""
MODULE: mcp_transport_service
PURPOSE: MCP transport metadata only (no live server) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_mcp_transport_manifest() -> dict[str, Any]:
    return {
        "supported_transports": [
            {"transport": "stdio", "supported_now": True, "notes": "metadata only"},
            {"transport": "http_sse", "supported_now": False, "notes": "deferred: no public MCP server"},
            {"transport": "websocket", "supported_now": False, "notes": "deferred: no public MCP server"},
        ],
        "public_mcp_server_required_now": False,
        "external_execution_enabled": False,
        "deterministic": True,
    }

