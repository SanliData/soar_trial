"""
MODULE: mcp_capability_registry
PURPOSE: MCP-compatible capability projection registry (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.semantic_capabilities.capability_loader import load_capabilities


def export_mcp_capability_registry(*, policy_scope: str = "internal_operator") -> dict[str, Any]:
    """
    Compatibility abstraction:
    - exposes internal capability metadata in MCP-friendly shape
    - does NOT run tools
    """
    caps = load_capabilities()
    rows = []
    for c in caps:
        rows.append(
            {
                "capability_id": c.capability_id,
                "name": c.name,
                "domain": c.domain,
                "endpoint": c.endpoint,
                "http_method": c.http_method,
                "orchestration_safe": c.orchestration_safe,
                "destructive_action": c.destructive_action,
                "human_approval_required": c.human_approval_required,
                "policy_scope": policy_scope,
            }
        )
    return {
        "capabilities": rows,
        "projection_schema": "mcp_capability_projection_v1",
        "policy_scoped": True,
        "deterministic": True,
        "no_external_execution": True,
    }

