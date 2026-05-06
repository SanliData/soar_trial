"""
MODULE: workflow_intent_router
PURPOSE: Deterministic mapping from intent to workflow categories (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

WORKFLOW_CATEGORIES = (
    "procurement_analysis",
    "contractor_ranking",
    "permit_monitoring",
    "onboarding_generation",
    "executive_reporting",
    "graph_investigation",
)


def route_workflow_intent(parsed_intent: str, workflow_scope_hint: str | None = None) -> dict[str, Any]:
    intent = (parsed_intent or "").strip()
    hint = (workflow_scope_hint or "").strip()
    routed = hint if hint in WORKFLOW_CATEGORIES else None
    if routed is None and intent in WORKFLOW_CATEGORIES:
        routed = intent
    if routed is None:
        routed = "executive_reporting"
    return {
        "parsed_intent": intent,
        "workflow_scope_hint": hint or None,
        "routed_workflow": routed,
        "routing_policy": "static_mapping_v1",
        "deterministic": True,
        "explainable": True,
    }

