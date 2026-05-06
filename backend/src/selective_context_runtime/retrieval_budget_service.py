"""
MODULE: retrieval_budget_service
PURPOSE: Explicit retrieval budgets and limits (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


_BUDGETS: list[dict[str, Any]] = [
    {
        "workflow_name": "procurement_analysis",
        "max_retrieval_tokens": 8000,
        "max_expanded_chunks": 6,
        "compression_required": True,
        "expansion_policy": "selective_expansion",
    },
    {
        "workflow_name": "contractor_ranking",
        "max_retrieval_tokens": 6000,
        "max_expanded_chunks": 4,
        "compression_required": True,
        "expansion_policy": "selective_expansion",
    },
    {
        "workflow_name": "executive_reporting",
        "max_retrieval_tokens": 5000,
        "max_expanded_chunks": 3,
        "compression_required": True,
        "expansion_policy": "summary_only",
    },
]


def export_retrieval_budgets() -> dict[str, Any]:
    return {
        "budgets": [dict(b) for b in _BUDGETS],
        "explicit_limits": True,
        "unlimited_retrieval_expansion": False,
        "deterministic": True,
    }


def get_budget(workflow_name: str) -> dict[str, Any]:
    wf = (workflow_name or "").strip()
    for b in _BUDGETS:
        if b["workflow_name"] == wf:
            return dict(b)
    raise ValueError("unknown workflow budget")

