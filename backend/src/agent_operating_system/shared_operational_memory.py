"""
MODULE: shared_operational_memory
PURPOSE: Shared operational memory (governed metadata only) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_operational_memory_item(item: dict[str, Any]) -> None:
    if not isinstance(item, dict):
        raise ValueError("invalid memory item")
    required = {
        "memory_id",
        "memory_type",
        "workspace_scope",
        "content_summary",
        "source_lineage",
        "access_scope",
        "created_at",
    }
    if required - item.keys():
        raise ValueError("memory item missing required fields")
    if not isinstance(item.get("access_scope"), str) or not item["access_scope"].strip():
        raise ValueError("access_scope required")
    lineage = item.get("source_lineage")
    if not isinstance(lineage, dict) or not lineage:
        raise ValueError("source_lineage required")


def export_shared_operational_memory_manifest() -> dict[str, Any]:
    sample = {
        "memory_id": "mem-001",
        "memory_type": "command_audit",
        "workspace_scope": "executive_reporting",
        "content_summary": "Command center audit metadata stored; no raw secrets.",
        "source_lineage": {"source_type": "command_audit_log", "source_record_id": "cmd-001"},
        "access_scope": "workflow_scoped_read",
        "created_at": "2026-01-01T00:00:00Z",
    }
    validate_operational_memory_item(sample)
    return {
        "memory_items": [sample],
        "no_unrestricted_shared_memory": True,
        "deterministic": True,
    }

