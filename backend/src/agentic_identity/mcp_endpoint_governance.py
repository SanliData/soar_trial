"""
MODULE: mcp_endpoint_governance
PURPOSE: MCP endpoint governance metadata (no unrestricted exposure) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_mcp_endpoint_governance() -> dict[str, Any]:
    endpoints = [
        {
            "endpoint_id": "mcp-gw-projection-only",
            "endpoint_scope": "projection_only",
            "allowed_capabilities": ["context.*", "mcp.*", "system.visibility.*"],
            "runtime_budget": {"max_tokens": 24000, "deterministic": True},
            "connector_scope": {"allowed": ["uploaded_documents"], "deterministic": True},
            "approval_requirements": {"human_approval_required": False, "deterministic": True},
            "exposure_risk": "low",
            "unrestricted_mcp_endpoint_exposure": False,
            "deterministic": True,
        }
    ]
    return {"mcp_endpoints": endpoints, "deterministic": True, "governance_metadata_mandatory": True}

