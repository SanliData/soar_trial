"""
MODULE: workspace_command_registry
PURPOSE: Deterministic operational commands — scoped execution semantics (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

WORKSPACE_COMMAND_EPOCH = "2025-05-01T00:00:00Z"

WORKSPACE_COMMANDS: dict[str, dict[str, Any]] = {
    "analyze_opportunity": {
        "command_id": "analyze_opportunity",
        "required_workspace_scope": "procurement_sales",
        "risk_band": "medium",
        "scoped_execution": True,
        "created_at": WORKSPACE_COMMAND_EPOCH,
    },
    "rank_contractors": {
        "command_id": "rank_contractors",
        "required_workspace_scope": "procurement_sales",
        "risk_band": "high",
        "scoped_execution": True,
        "created_at": WORKSPACE_COMMAND_EPOCH,
    },
    "validate_workflow": {
        "command_id": "validate_workflow",
        "required_workspace_scope": "any_governed",
        "risk_band": "low",
        "scoped_execution": True,
        "created_at": WORKSPACE_COMMAND_EPOCH,
    },
    "trace_reliability": {
        "command_id": "trace_reliability",
        "required_workspace_scope": "intel_graph_read",
        "risk_band": "low",
        "scoped_execution": True,
        "created_at": WORKSPACE_COMMAND_EPOCH,
    },
    "generate_onboarding": {
        "command_id": "generate_onboarding",
        "required_workspace_scope": "customer_onboarding",
        "risk_band": "medium",
        "scoped_execution": True,
        "created_at": WORKSPACE_COMMAND_EPOCH,
    },
}


def export_workspace_commands_manifest() -> list[dict[str, Any]]:
    return [dict(WORKSPACE_COMMANDS[k]) for k in sorted(WORKSPACE_COMMANDS.keys())]


def get_workspace_command(command_id: str) -> dict[str, Any] | None:
    key = command_id.strip()
    if key not in WORKSPACE_COMMANDS:
        return None
    return dict(WORKSPACE_COMMANDS[key])
