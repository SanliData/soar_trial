"""
MODULE: skill_validation_service
PURPOSE: Validate skills and reject unsafe inheritance / spawning metadata (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_registry_service import SKILL_REGISTRY


def validate_skill_name(skill_name: str) -> None:
    key = skill_name.strip()
    if key not in SKILL_REGISTRY:
        raise ValueError("invalid skill")


def validate_unsafe_skill_runtime_metadata(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unrestricted_skill_spawning") is True:
        raise ValueError("unsafe skill metadata rejected")
    if meta.get("recursive_workflow_mutation") is True:
        raise ValueError("unsafe skill metadata rejected")
    if meta.get("hidden_tool_escalation") is True:
        raise ValueError("unsafe skill metadata rejected")
