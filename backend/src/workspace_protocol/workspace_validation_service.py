"""
MODULE: workspace_validation_service
PURPOSE: Validate workspace artifacts and reject unsafe scopes (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.workspace_protocol.workspace_policy_registry import WORKSPACE_POLICIES


def validate_workspace_policy_name(policy_name: str) -> None:
    key = policy_name.strip()
    if key not in WORKSPACE_POLICIES:
        raise ValueError("invalid workspace policy")


def validate_unsafe_workspace_metadata(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unrestricted_persistent_memory") is True:
        raise ValueError("unsafe workspace metadata rejected")
    if meta.get("autonomous_workspace_mutation") is True:
        raise ValueError("unsafe workspace metadata rejected")
    if meta.get("uncontrolled_agent_spawning") is True:
        raise ValueError("unsafe workspace metadata rejected")


def validate_memory_access_projection(visibility_requested: str) -> None:
    allowed = frozenset(
        {"workspace_scoped", "session_ttl", "project_lead_only", "evaluation_role", "architecture_contract"}
    )
    if visibility_requested.strip() not in allowed:
        raise ValueError("invalid memory visibility projection")
