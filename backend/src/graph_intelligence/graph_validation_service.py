"""
MODULE: graph_validation_service
PURPOSE: Reject autonomous graph mutation configs (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_graph_operation_intent(intent: dict[str, Any] | None) -> None:
    if not intent:
        return
    if intent.get("autonomous_graph_mutation") is True:
        raise ValueError("autonomous graph mutation rejected")
    if intent.get("write_without_human_gate") is True and intent.get("production_graph") is True:
        raise ValueError("unsafe graph write intent")


def validate_traversal_depth(requested_depth: int) -> int:
    if requested_depth < 1 or requested_depth > 64:
        raise ValueError("invalid traversal depth hint")
    return requested_depth
