"""
MODULE: runtime_token_budget_service
PURPOSE: Token budgets per category — explicit overflow policy (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_CATEGORIES = (
    "orchestration",
    "reflection",
    "evaluation",
    "ensemble_evaluation",
    "skill_activation",
    "retrieval",
    "graph_reasoning",
)

_DEFAULT_BUDGETS: dict[str, dict[str, Any]] = {
    "orchestration": {"budget_tokens": 24000, "hard_cap_tokens": 28000},
    "reflection": {"budget_tokens": 8000, "hard_cap_tokens": 9600},
    "evaluation": {"budget_tokens": 12000, "hard_cap_tokens": 14400},
    "ensemble_evaluation": {"budget_tokens": 6000, "hard_cap_tokens": 7200},
    "skill_activation": {"budget_tokens": 16000, "hard_cap_tokens": 19200},
    "retrieval": {"budget_tokens": 10000, "hard_cap_tokens": 12000},
    "graph_reasoning": {"budget_tokens": 14000, "hard_cap_tokens": 16800},
}


def export_runtime_token_budgets_manifest() -> dict[str, Any]:
    rows = []
    for cat in sorted(_CATEGORIES):
        b = dict(_DEFAULT_BUDGETS[cat])
        b["category"] = cat
        b["overflow_policy"] = "fail_closed_report_to_telemetry"
        b["unlimited_expansion_allowed"] = False
        rows.append(b)
    return {
        "categories": rows,
        "overflow_handling_explicit": True,
        "ensemble_aware_budgeting": True,
        "h043_sparse_context_cross_ref": True,
        "deterministic": True,
    }


def categorize_budget(category: str) -> dict[str, Any]:
    key = category.strip()
    if key not in _DEFAULT_BUDGETS:
        raise ValueError("invalid budget category")
    return dict(_DEFAULT_BUDGETS[key])
