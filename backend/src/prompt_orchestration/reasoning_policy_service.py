"""
MODULE: reasoning_policy_service
PURPOSE: Deterministic task → strategy mapping with rationale keys (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

TASK_TO_STRATEGY: dict[str, str] = {
    "graph_reasoning": "arq_reasoning",
    "widget_generation": "json_prompting",
    "executive_summary": "constrained_summary",
    "onboarding_planner": "role_prompting",
    "market_signal_analysis": "arq_reasoning",
    "opportunity_ranking": "json_prompting",
    "procurement_review": "arq_reasoning",
    "results_hub_packaging": "json_prompting",
    "general_qa": "direct_prompting",
}

DEFAULT_STRATEGY = "direct_prompting"

RATIONALE_BY_TASK: dict[str, str] = {
    "graph_reasoning": "Graph tasks require checklist-bound ARQ traversal.",
    "widget_generation": "Widget payloads must satisfy JSON contracts.",
    "executive_summary": "Executive surfaces require constrained summarisation.",
    "onboarding_planner": "Onboarding flows use approved specialist personas.",
    "market_signal_analysis": "Signals validated via ARQ market checklist.",
    "opportunity_ranking": "Ranked outputs map to JSON opportunity contract.",
    "procurement_review": "Procurement uses ARQ procurement checklist.",
    "results_hub_packaging": "Results Hub bundles require JSON schema adherence.",
    "general_qa": "Fallback direct prompting when no specialised policy applies.",
}


def select_strategy_for_task(task_type: str) -> dict[str, Any]:
    tt = task_type.strip().lower().replace(" ", "_")
    strat = TASK_TO_STRATEGY.get(tt, DEFAULT_STRATEGY)
    rationale = RATIONALE_BY_TASK.get(tt, "Default policy: unknown task uses direct prompting.")
    return {
        "task_type": task_type,
        "recommended_strategy": strat,
        "rationale": rationale,
        "policy_rule": f"task:{tt}->strategy:{strat}",
    }
