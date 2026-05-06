"""
MODULE: sensitive_action_guard_service
PURPOSE: High-risk operation guards — mandatory interception (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_SENSITIVE_ACTIONS: dict[str, dict[str, Any]] = {
    "mass_delete": {
        "action_id": "mass_delete",
        "interception": "mandatory",
        "approval_aware": True,
        "dual_control_default": True,
    },
    "bulk_export": {
        "action_id": "bulk_export",
        "interception": "mandatory",
        "approval_aware": True,
        "dual_control_default": False,
    },
    "external_submit": {
        "action_id": "external_submit",
        "interception": "mandatory",
        "approval_aware": True,
        "dual_control_default": True,
    },
    "graph_rewrite": {
        "action_id": "graph_rewrite",
        "interception": "mandatory",
        "approval_aware": True,
        "dual_control_default": True,
    },
    "workflow_override": {
        "action_id": "workflow_override",
        "interception": "mandatory",
        "approval_aware": True,
        "dual_control_default": True,
    },
}


def export_protected_actions_manifest() -> list[dict[str, Any]]:
    return [dict(_SENSITIVE_ACTIONS[k]) for k in sorted(_SENSITIVE_ACTIONS.keys())]


def validate_protected_action(action_id: str) -> None:
    if action_id.strip() not in _SENSITIVE_ACTIONS:
        raise ValueError("unknown protected action")


def assess_sensitive_action(action_id: str, human_approval_present: bool) -> dict[str, Any]:
    validate_protected_action(action_id)
    cfg = _SENSITIVE_ACTIONS[action_id.strip()]
    if cfg["approval_aware"] and not human_approval_present:
        return {"intercepted": True, "reason": "approval_required", "deterministic": True}
    return {"intercepted": False, "reason": None, "deterministic": True}
