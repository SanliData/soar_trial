"""
MODULE: retrieval_fallback_service
PURPOSE: Retrieval-first recommendations when context unsafe — no workflow rewrite (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.long_context_runtime.context_pressure_service import classify_context_pressure


def recommend_retrieval_fallback(*, pressure_metrics: dict[str, Any], runtime_budget_ok: bool) -> dict[str, Any]:
    pr = classify_context_pressure(pressure_metrics)
    pressure_level = pr["pressure_level"]
    recommend = pressure_level in {"high", "critical"} or not runtime_budget_ok
    return {
        "recommend_retrieval_first": recommend,
        "pressure_level": pressure_level,
        "runtime_budget_ok": runtime_budget_ok,
        "autonomous_workflow_rewriting": False,
        "deterministic": True,
    }


def export_retrieval_fallback_manifest() -> dict[str, Any]:
    return {
        "examples": [
            recommend_retrieval_fallback(
                pressure_metrics={
                    "context_window_tokens": 90000,
                    "retrieval_doc_breadth": 8,
                    "duplicated_blocks": 2,
                    "reflection_share": 0.15,
                    "orchestration_depth_hint": 4,
                },
                runtime_budget_ok=False,
            ),
            recommend_retrieval_fallback(
                pressure_metrics={
                    "context_window_tokens": 6000,
                    "retrieval_doc_breadth": 4,
                    "duplicated_blocks": 0,
                    "reflection_share": 0.08,
                    "orchestration_depth_hint": 2,
                },
                runtime_budget_ok=True,
            ),
        ],
        "deterministic": True,
    }
