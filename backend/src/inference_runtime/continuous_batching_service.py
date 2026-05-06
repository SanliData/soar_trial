"""
MODULE: continuous_batching_service
PURPOSE: Batching abstractions — deterministic metadata only (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_BATCH_GROUPS: list[dict[str, Any]] = [
    {
        "workflow_group_id": "wg_orchestration_read",
        "workflows": ["lead_generation_v1", "graph_readonly_explain"],
        "batching_eligible": True,
        "token_pooling_budget": 32000,
        "latency_budget_ms_p95": 800,
        "batch_efficiency_score": 0.82,
    },
    {
        "workflow_group_id": "wg_skill_activation_serial",
        "workflows": ["procurement_review", "reliability_audit"],
        "batching_eligible": False,
        "token_pooling_budget": 0,
        "latency_budget_ms_p95": 1200,
        "batch_efficiency_score": 0.0,
        "ineligibility_reason": "serial_skill_activation_contract",
    },
]


def export_continuous_batching_manifest() -> dict[str, Any]:
    return {
        "workflow_groups": [dict(g) for g in _BATCH_GROUPS],
        "abstraction_only": True,
        "autonomous_scheduler": False,
        "deterministic": True,
    }
