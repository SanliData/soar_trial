"""
MODULE: memory_context_service
PURPOSE: Memory context manifest (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_memory_context(
    *,
    context_id: str,
    workflow_scope: str,
    summary: str,
    source_type: str,
    source_record_id: str,
    priority: int = 50,
    isolation_required: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "memory_context",
        "workflow_scope": workflow_scope,
        "content_summary": (summary or "").strip()[:320],
        "source_lineage": {"source_type": source_type, "source_record_id": source_record_id},
        "priority": int(priority),
        "token_estimate": max(0, int(len(summary or "") / 4)),
        "isolation_required": bool(isolation_required),
        "compression_allowed": True,
        # Deterministic epoch required for governed foundation + repeatable tests.
        "created_at": "2026-01-01T00:00:00Z",
        "tags": list(tags or ["memory"]),
    }
    validate_context_item(item)
    return item


def export_memory_context_examples() -> list[dict[str, Any]]:
    return [
        build_memory_context(
            context_id="ctx-mem-001",
            workflow_scope="onboarding_generation",
            summary="User requested bilingual (EN/TR) onboarding checklist; avoid any secrets in output.",
            source_type="workflow_checkpoint",
            source_record_id="wf-onboarding-2026-05-06#1",
            priority=55,
            isolation_required=True,
            tags=["memory", "onboarding"],
        )
    ]

