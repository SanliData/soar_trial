"""
MODULE: tool_context_service
PURPOSE: Tool context manifest with capability references (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_tool_context(
    *,
    context_id: str,
    workflow_scope: str,
    summary: str,
    capability_references: list[str],
    priority: int = 65,
    isolation_required: bool = True,
    compression_allowed: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "tool_context",
        "workflow_scope": workflow_scope,
        "content_summary": (summary or "").strip()[:320],
        "source_lineage": {},
        "priority": int(priority),
        "token_estimate": max(0, int(len(summary or "") / 4)) + 40,
        "isolation_required": bool(isolation_required),
        "compression_allowed": bool(compression_allowed),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": list(tags or ["tools"]),
        "capability_references": list(capability_references),
    }
    validate_context_item(item)
    return item


def export_tool_context_examples() -> list[dict[str, Any]]:
    return [
        build_tool_context(
            context_id="ctx-tool-001",
            workflow_scope="procurement_analysis",
            summary="Use capability catalog for allowed read-only endpoints; do not execute external tools.",
            capability_references=["context.types", "context.lifecycle", "documents.ocr_pipeline", "mcp.tools"],
            priority=70,
            isolation_required=True,
            compression_allowed=True,
            tags=["tools", "capabilities"],
        )
    ]

