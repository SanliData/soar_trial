"""
MODULE: subagent_boundary_service
PURPOSE: Explicit scope/permission gates — bounded spawning (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_SCOPES: frozenset[str] = frozenset({"read_only", "graph_local", "results_hub", "onboarding_flow"})
REQUIRED_PERMISSION_PREFIXES: tuple[str, ...] = ("read:", "execute:", "delegate:")
MAX_SUBAGENTS_PER_SESSION: int = 4


def validate_subagent_spawn(current_count: int, scope: str, permissions: list[str]) -> dict[str, Any]:
    if current_count >= MAX_SUBAGENTS_PER_SESSION:
        raise ValueError("sub-agent spawn limit reached for session (foundation cap)")
    if scope not in ALLOWED_SCOPES:
        raise ValueError(f"scope not allowed: {scope}")
    if not permissions:
        raise ValueError("permissions list required — empty not permitted")
    ok = any(str(p).startswith(REQUIRED_PERMISSION_PREFIXES) for p in permissions)
    if not ok:
        raise ValueError("permissions must use approved prefixes (read:, execute:, delegate:)")
    return {
        "spawn_ok": True,
        "scope": scope,
        "permission_count": len(permissions),
        "foundation_cap": MAX_SUBAGENTS_PER_SESSION,
    }


def describe_boundaries() -> dict[str, Any]:
    return {
        "max_subagents_per_session": MAX_SUBAGENTS_PER_SESSION,
        "allowed_scopes": sorted(ALLOWED_SCOPES),
        "permission_prefixes": list(REQUIRED_PERMISSION_PREFIXES),
    }
