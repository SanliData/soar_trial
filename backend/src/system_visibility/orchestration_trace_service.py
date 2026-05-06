"""
MODULE: orchestration_trace_service
PURPOSE: Explainable orchestration traces across workflows (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_command_center import build_command_center_manifest
from src.federated_retrieval.federated_search_service import federated_search
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion
from src.skill_runtime.skill_activation_service import export_skill_activation_manifest


def export_orchestration_trace() -> dict[str, Any]:
    """
    Trace is explainable metadata only — no hidden orchestration or execution.
    """
    command = build_command_center_manifest("Review procurement bid and export summary")
    retrieval = federated_search(query="procurement notice", mode="hybrid", limit=3)
    expansion = decide_selective_expansion(
        workflow_name="procurement_analysis",
        query="deadline scope",
        chunks=[
            {"chunk_id": "c1", "text": "submission deadline scope", "source_lineage": {"authority_score": 0.88, "freshness_days": 3}},
            {"chunk_id": "c2", "text": "unrelated", "source_lineage": {"authority_score": 0.55, "freshness_days": 21}},
        ],
    )
    skills = export_skill_activation_manifest()

    chain = [
        {"step_id": "t1", "type": "nl_command_routing", "detail": {"intent": command["intent"]}, "deterministic": True},
        {"step_id": "t2", "type": "approval_detection", "detail": command["approval"], "deterministic": True},
        {"step_id": "t3", "type": "skill_activation_metadata", "detail": {"skills": skills}, "deterministic": True},
        {"step_id": "t4", "type": "retrieval", "detail": {"results": retrieval["results"]}, "deterministic": True},
        {"step_id": "t5", "type": "selective_expansion", "detail": expansion, "deterministic": True},
    ]

    return {
        "workflow_chain": chain,
        "no_hidden_orchestration": True,
        "recommendation_only": True,
        "deterministic": True,
    }
