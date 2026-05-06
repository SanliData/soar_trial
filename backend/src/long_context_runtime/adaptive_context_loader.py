"""
MODULE: adaptive_context_loader
PURPOSE: Importance-aware operational context loading plans — no full-context default (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_adaptive_context_loader_manifest() -> dict[str, Any]:
    return {
        "loading_policy": "importance_weighted_partition_first",
        "partitions_considered": ["procurement_documents", "contractor_history", "workflow_memory"],
        "prioritization_rules": [
            {"rule_id": "r1", "description": "User-anchored entities before background corpora."},
            {"rule_id": "r2", "description": "Truncate tail documents when pressure exceeds moderate."},
        ],
        "context_reduction_recommendations": [
            {"trigger": "pressure_high", "action": "defer_low_weight_partitions"},
            {"trigger": "retrieval_feasible", "action": "retrieval_first_skeleton"},
        ],
        "runtime_load_balancing_metadata": {
            "max_concurrent_partition_loads": 2,
            "serial_prefill_when_pressure_critical": True,
        },
        "full_context_default_loading": False,
        "deterministic_prioritization": True,
        "explainable_loading_decisions": True,
        "deterministic": True,
    }
