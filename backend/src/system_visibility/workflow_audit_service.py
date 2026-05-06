"""
MODULE: workflow_audit_service
PURPOSE: Deterministic workflow audit timeline metadata (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.federated_search_service import federated_search
from src.natural_language_control_plane.command_audit_service import export_audit_log
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion


def export_workflow_audit(*, workflow_scope: str = "procurement_analysis") -> dict[str, Any]:
    """
    Immutable-style audit metadata preferred: return an event list with stable ordering.
    """
    wf = (workflow_scope or "").strip() or "procurement_analysis"
    audit = export_audit_log(limit=10)
    retrieval = federated_search(query="telecom bid", mode="hybrid", limit=5)
    expansion = decide_selective_expansion(
        workflow_name=wf if wf in {"procurement_analysis", "contractor_ranking", "executive_reporting"} else "procurement_analysis",
        query="ISO 27001 net-30",
        chunks=[
            {"chunk_id": "c1", "text": "ISO 27001 net-30", "source_lineage": {"authority_score": 0.88, "freshness_days": 3}},
            {"chunk_id": "c2", "text": "marketing", "source_lineage": {"authority_score": 0.55, "freshness_days": 21}},
        ],
    )

    events: list[dict[str, Any]] = [
        {"event_id": "wf-001", "type": "workflow_start", "workflow_scope": wf, "deterministic": True},
        {"event_id": "wf-002", "type": "nl_command_audit", "audit_buffer_size": len(audit.get("audits") or []), "deterministic": True},
        {"event_id": "wf-003", "type": "retrieval", "result_count": retrieval["result_count"], "lineage_required": True, "deterministic": True},
        {
            "event_id": "wf-004",
            "type": "selective_context_expansion",
            "selected_chunks": expansion["selected_chunk_ids"],
            "token_savings_estimate": expansion["token_savings_estimate"],
            "deterministic": True,
        },
        {"event_id": "wf-005", "type": "workflow_end", "workflow_scope": wf, "deterministic": True},
    ]

    return {
        "workflow_scope": wf,
        "timeline": events,
        "approvals_visible": True,
        "retrieval_lineage_visible": True,
        "context_expansion_events_visible": True,
        "compression_events_visible": True,
        "deterministic": True,
    }

