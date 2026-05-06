"""
MODULE: guardrail_context_service
PURPOSE: Guardrail context manifest (never implicitly compressed away) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_guardrail_context(
    *,
    context_id: str,
    workflow_scope: str,
    guardrails: str,
    priority: int = 100,
    isolation_required: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "guardrail_context",
        "workflow_scope": workflow_scope,
        "content_summary": (guardrails or "").strip()[:360],
        "source_lineage": {},
        "priority": int(priority),
        "token_estimate": max(0, int(len(guardrails or "") / 4)),
        "isolation_required": bool(isolation_required),
        "compression_allowed": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": list(tags or ["guardrails"]),
    }
    validate_context_item(item)
    return item


def export_guardrail_context_examples() -> list[dict[str, Any]]:
    return [
        build_guardrail_context(
            context_id="ctx-gr-001",
            workflow_scope="procurement_analysis",
            guardrails=(
                "No uncontrolled external execution. No secrets. "
                "Keep context typed (instructions/examples/knowledge/memory/tools/guardrails). "
                "Guardrails must remain visible separately."
            ),
            priority=100,
            isolation_required=True,
            tags=["guardrails", "h044"],
        )
    ]

