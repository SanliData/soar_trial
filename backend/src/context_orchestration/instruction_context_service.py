"""
MODULE: instruction_context_service
PURPOSE: Instruction context manifest (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.context_orchestration.context_validation_service import validate_context_item


def build_instruction_context(
    *,
    context_id: str,
    workflow_scope: str,
    instructions: str,
    priority: int = 80,
    isolation_required: bool = True,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "context_id": context_id,
        "context_type": "instruction_context",
        "workflow_scope": workflow_scope,
        "content_summary": (instructions or "").strip()[:280],
        "source_lineage": {},
        "priority": int(priority),
        "token_estimate": max(0, int(len(instructions or "") / 4)),
        "isolation_required": bool(isolation_required),
        "compression_allowed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tags": list(tags or ["instructions"]),
    }
    validate_context_item(item)
    return item


def export_instruction_context_examples() -> list[dict[str, Any]]:
    return [
        build_instruction_context(
            context_id="ctx-inst-001",
            workflow_scope="procurement_analysis",
            instructions="Provide an auditable procurement summary with citations and no uncontrolled execution.",
            priority=90,
            isolation_required=True,
            tags=["instructions", "procurement"],
        ),
    ]

