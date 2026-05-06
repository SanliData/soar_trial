"""
MODULE: evaluation_router
PURPOSE: Deterministic workflow → evaluation destination routing (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

***REMOVED*** Workflow label → evaluation subsystem — static mapping only.
WORKFLOW_EVALUATION_ROUTES: dict[str, str] = {
    "graph": "graph_evaluation",
    "graph_reasoning": "graph_evaluation",
    "onboarding": "onboarding_evaluation",
    "executive_briefing": "briefing_evaluation",
    "results_hub": "results_hub_evaluation",
    "market_signals": "signal_evaluation",
    "default": "generic_evaluation",
}


def route_evaluation(workflow_type: str) -> dict[str, Any]:
    key = workflow_type.strip().lower() if workflow_type else "default"
    target = WORKFLOW_EVALUATION_ROUTES.get(key, WORKFLOW_EVALUATION_ROUTES["default"])
    return {
        "workflow_type": workflow_type,
        "evaluation_target": target,
        "routing_rule": "static_lookup_v1",
    }


def list_routes() -> dict[str, Any]:
    return {"routes": dict(sorted(WORKFLOW_EVALUATION_ROUTES.items()))}
