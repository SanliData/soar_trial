"""
MODULE: example_context_service
PURPOSE: Example context manifest (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_example_context(
    *,
    context_id: str,
    workflow_scope: str,
    example: str,
    priority: int = 60,
    isolation_required: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "example_context",
        "workflow_scope": workflow_scope,
        "content_summary": (example or "").strip()[:280],
        "source_lineage": {},
        "priority": int(priority),
        "token_estimate": max(0, int(len(example or "") / 4)),
        "isolation_required": bool(isolation_required),
        "compression_allowed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": list(tags or ["examples"]),
    }
    validate_context_item(item)
    return item


def export_example_context_examples() -> list[dict[str, Any]]:
    return [
        build_example_context(
            context_id="ctx-ex-001",
            workflow_scope="executive_reporting",
            example="Output format: {\"summary\": \"...\", \"risks\": [...], \"next_steps\": [...]}",
            priority=55,
            isolation_required=True,
            tags=["examples", "format"],
        )
    ]

