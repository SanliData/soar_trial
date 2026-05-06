"""
MODULE: context_validation_service
PURPOSE: Typed context schema validation and governance (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

ALLOWED_CONTEXT_TYPES: frozenset[str] = frozenset(
    {
        "instruction_context",
        "example_context",
        "knowledge_context",
        "memory_context",
        "tool_context",
        "guardrail_context",
    }
)


def validate_context_type(context_type: str) -> None:
    ct = (context_type or "").strip()
    if ct not in ALLOWED_CONTEXT_TYPES:
        raise ValueError("invalid context_type rejected")


def _require_nonempty_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"invalid {field}")
    return value.strip()


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"invalid {field}")
    return value


def _require_int(value: Any, field: str) -> int:
    if not isinstance(value, int):
        raise ValueError(f"invalid {field}")
    return value


def validate_context_item(item: dict[str, Any]) -> None:
    """
    Validates the common H-044 typed context fields.

    This is intentionally a lightweight, deterministic validator (no model calls).
    """
    if not isinstance(item, dict):
        raise ValueError("context item must be a dict")

    context_id = _require_nonempty_str(item.get("context_id"), "context_id")
    if len(context_id) > 200:
        raise ValueError("invalid context_id")

    context_type = _require_nonempty_str(item.get("context_type"), "context_type")
    validate_context_type(context_type)

    _require_nonempty_str(item.get("workflow_scope"), "workflow_scope")
    _require_nonempty_str(item.get("content_summary"), "content_summary")

    # lineage is required for knowledge/memory
    source_lineage = item.get("source_lineage")
    if context_type in {"knowledge_context", "memory_context"}:
        if not isinstance(source_lineage, dict) or not source_lineage:
            raise ValueError("source_lineage required for knowledge/memory context")
        _require_nonempty_str(source_lineage.get("source_type"), "source_lineage.source_type")
        _require_nonempty_str(source_lineage.get("source_record_id"), "source_lineage.source_record_id")

    # tool_context must reference capabilities
    if context_type == "tool_context":
        caps = item.get("capability_references")
        if not isinstance(caps, list) or not caps or not all(isinstance(x, str) and x.strip() for x in caps):
            raise ValueError("tool_context requires capability_references")

    # guardrails are special: never allow implicit compression
    compression_allowed = _require_bool(item.get("compression_allowed"), "compression_allowed")
    if context_type == "guardrail_context" and compression_allowed is True:
        raise ValueError("guardrail_context must not be compressible by default")

    _require_int(item.get("priority"), "priority")
    token_estimate = _require_int(item.get("token_estimate"), "token_estimate")
    if token_estimate < 0:
        raise ValueError("invalid token_estimate")

    _require_bool(item.get("isolation_required"), "isolation_required")

    created_at = item.get("created_at")
    if not isinstance(created_at, str) or not created_at.strip():
        raise ValueError("invalid created_at")
    try:
        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid created_at") from exc

    tags = item.get("tags")
    if not isinstance(tags, list) or not all(isinstance(x, str) for x in tags):
        raise ValueError("invalid tags")


def validate_context_collection(items: list[dict[str, Any]]) -> None:
    if not isinstance(items, list):
        raise ValueError("context collection must be a list")
    for it in items:
        validate_context_item(it)

