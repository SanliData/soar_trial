"""
MODULE: workflow_context_partitioning
PURPOSE: Deterministic workflow-to-context partitions (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


_WORKFLOW_PARTITIONS: dict[str, dict[str, Any]] = {
    "procurement_analysis": {
        "workflow_scope": "procurement_analysis",
        "allowed_context_types": [
            "instruction_context",
            "example_context",
            "knowledge_context",
            "memory_context",
            "tool_context",
            "guardrail_context",
        ],
        "isolation_required": True,
    },
    "onboarding_generation": {
        "workflow_scope": "onboarding_generation",
        "allowed_context_types": [
            "instruction_context",
            "example_context",
            "knowledge_context",
            "memory_context",
            "tool_context",
            "guardrail_context",
        ],
        "isolation_required": True,
    },
    "graph_investigation": {
        "workflow_scope": "graph_investigation",
        "allowed_context_types": [
            "instruction_context",
            "example_context",
            "knowledge_context",
            "memory_context",
            "tool_context",
            "guardrail_context",
        ],
        "isolation_required": True,
    },
    "executive_reporting": {
        "workflow_scope": "executive_reporting",
        "allowed_context_types": [
            "instruction_context",
            "example_context",
            "knowledge_context",
            "memory_context",
            "tool_context",
            "guardrail_context",
        ],
        "isolation_required": True,
    },
    "contractor_ranking": {
        "workflow_scope": "contractor_ranking",
        "allowed_context_types": [
            "instruction_context",
            "example_context",
            "knowledge_context",
            "memory_context",
            "tool_context",
            "guardrail_context",
        ],
        "isolation_required": True,
    },
}


def export_workflow_partitions() -> dict[str, Any]:
    return {
        "workflows": [dict(_WORKFLOW_PARTITIONS[k]) for k in sorted(_WORKFLOW_PARTITIONS.keys())],
        "no_unrestricted_shared_context": True,
        "deterministic": True,
    }


def get_partition(workflow_scope: str) -> dict[str, Any]:
    key = (workflow_scope or "").strip()
    if key not in _WORKFLOW_PARTITIONS:
        raise ValueError("unknown workflow_scope")
    return dict(_WORKFLOW_PARTITIONS[key])

