"""
MODULE: mcp_runtime_validation
PURPOSE: Reject unsafe MCP projections (policy-scoped tools only) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_mcp_projection_policy(policy_scope: str) -> None:
    ps = (policy_scope or "").strip()
    if ps not in {"internal_operator", "governed_readonly"}:
        raise ValueError("invalid policy scope")


def validate_mcp_tool_projection(tool: dict[str, Any]) -> None:
    if not isinstance(tool, dict):
        raise ValueError("invalid tool projection")
    for key in ("tool_id", "name", "capability_id", "policy_scope"):
        if not isinstance(tool.get(key), str) or not tool[key].strip():
            raise ValueError("invalid tool projection")
    validate_mcp_projection_policy(tool["policy_scope"])

    if tool.get("unrestricted_execution") is True:
        raise ValueError("unrestricted MCP execution rejected")
    if tool.get("external_execution_enabled") is True:
        raise ValueError("external MCP execution rejected")

