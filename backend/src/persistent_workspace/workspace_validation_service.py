"""
MODULE: workspace_validation_service
PURPOSE: Reject unsafe persistence intents (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.persistent_workspace.typed_state_registry import STATE_TYPES


def validate_state_type(state_type: str) -> None:
    if state_type.strip() not in STATE_TYPES:
        raise ValueError("invalid state type")


def validate_no_recursive_memory_expansion(intent: dict[str, Any] | None) -> None:
    if not intent:
        return
    if intent.get("recursive_memory_expansion") is True:
        raise ValueError("recursive memory expansion rejected")
    if intent.get("uncontrolled_persistent_execution") is True:
        raise ValueError("uncontrolled persistent execution rejected")


def validate_snapshot_depth(depth: int) -> None:
    if depth < 0 or depth > 32:
        raise ValueError("invalid snapshot depth")
