"""
MODULE: workspace_state_service
PURPOSE: Workspace operational state manifest (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.persistent_workspace.typed_state_registry import STATE_TYPES, export_typed_state_registry_manifest


def export_workspace_state_manifest() -> dict[str, Any]:
    return {
        "active_typed_slots": [f"slot:{t}" for t in STATE_TYPES],
        "registry": export_typed_state_registry_manifest(),
        "governance_version": "h042_workspace_v1",
        "uncontrolled_persistent_execution": False,
        "deterministic": True,
    }
