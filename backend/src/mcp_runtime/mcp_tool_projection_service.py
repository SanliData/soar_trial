"""
MODULE: mcp_tool_projection_service
PURPOSE: Project internal capabilities as MCP-like tools (no execution) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.mcp_runtime.mcp_runtime_validation import validate_mcp_tool_projection
from src.semantic_capabilities.capability_loader import load_capabilities


def project_mcp_tools(*, policy_scope: str = "internal_operator") -> dict[str, Any]:
    """
    Returns tool descriptors suitable for MCP-compatible runtimes.

    Rules:
    - projection only
    - no unrestricted external execution
    - policy-scoped
    """
    tools = []
    for c in load_capabilities():
        # projection allows read/projection operations; destructive is excluded by default
        if c.destructive_action:
            continue
        if not c.orchestration_safe:
            continue
        tool = {
            "tool_id": f"capability::{c.capability_id}",
            "name": c.name,
            "description": c.description,
            "capability_id": c.capability_id,
            "policy_scope": policy_scope,
            "invocation_surface": "http_get_projection_only",
            "endpoint": c.endpoint,
            "http_method": c.http_method,
            "requires_human_approval": bool(c.human_approval_required),
            "unrestricted_execution": False,
            "external_execution_enabled": False,
        }
        validate_mcp_tool_projection(tool)
        tools.append(tool)

    tools_sorted = sorted(tools, key=lambda t: t["tool_id"])
    digest = hashlib.sha256(json.dumps(tools_sorted, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return {
        "tools": tools_sorted,
        "tool_count": len(tools_sorted),
        "projection_schema": "mcp_tool_projection_v1",
        "policy_scope": policy_scope,
        "policy_scoped": True,
        "digest": digest,
        "deterministic": True,
    }

