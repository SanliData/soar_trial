"""
MODULE: adaptive_effort_service
PURPOSE: Deterministic reasoning-effort assignment (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

EFFORT_LEVELS: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")

# Task kind → effort (deterministic lookup).
_TASK_EFFORT_MAP: dict[str, str] = {
    "quick_lookup": "low",
    "lookup": "low",
    "procurement_analysis": "high",
    "onboarding_generation": "high",
    "onboarding_planning": "high",
    "graph_investigation": "xhigh",
    "executive_briefing": "max",
    "executive_audit": "max",
    "opportunity_ranking": "medium",
    "default": "medium",
}


def resolve_effort(task_kind: str, workflow_name: str | None = None) -> dict[str, Any]:
    """Return effort level with explainable routing rule."""
    key = (workflow_name or "").strip().lower()
    if key and key in _TASK_EFFORT_MAP:
        level = _TASK_EFFORT_MAP[key]
        rule = "workflow_name_lookup"
    else:
        tk = (task_kind or "default").strip().lower()
        level = _TASK_EFFORT_MAP.get(tk, _TASK_EFFORT_MAP["default"])
        rule = "task_kind_lookup" if tk in _TASK_EFFORT_MAP else "default_fallback"

    if level not in EFFORT_LEVELS:
        level = "medium"
        rule = "sanitized_invalid_level"

    return {
        "effort_level": level,
        "routing_rule": rule,
        "allowed_levels": list(EFFORT_LEVELS),
    }


def export_effort_manifest() -> dict[str, Any]:
    return {
        "levels": list(EFFORT_LEVELS),
        "examples": {
            "quick_lookup": "low",
            "onboarding_planning": "high",
            "graph_investigation": "xhigh",
            "executive_audit": "max",
        },
        "task_map": dict(sorted(_TASK_EFFORT_MAP.items())),
    }
