"""
MODULE: knowledge_context_service
PURPOSE: Knowledge context manifest (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_knowledge_context(
    *,
    context_id: str,
    workflow_scope: str,
    summary: str,
    source_type: str,
    source_record_id: str,
    parent_document_id: str | None = None,
    priority: int = 70,
    isolation_required: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "source_type": source_type,
        "source_record_id": source_record_id,
    }
    if parent_document_id:
        lineage["parent_document_id"] = parent_document_id
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "knowledge_context",
        "workflow_scope": workflow_scope,
        "content_summary": (summary or "").strip()[:360],
        "source_lineage": lineage,
        "priority": int(priority),
        "token_estimate": max(0, int(len(summary or "") / 4)),
        "isolation_required": bool(isolation_required),
        "compression_allowed": True,
        # Deterministic epoch required for governed foundation + repeatable tests.
        "created_at": "2026-01-01T00:00:00Z",
        "tags": list(tags or ["knowledge"]),
    }
    validate_context_item(item)
    return item


def export_knowledge_context_examples() -> list[dict[str, Any]]:
    return [
        build_knowledge_context(
            context_id="ctx-kn-001",
            workflow_scope="procurement_analysis",
            summary="Bid summary: vendor requires ISO 27001; payment net-30; delivery 12 weeks.",
            source_type="bid_pdf",
            source_record_id="bid-2026-0001",
            parent_document_id="doc-bid-0001",
            priority=75,
            isolation_required=True,
            tags=["knowledge", "bid"],
        )
    ]

