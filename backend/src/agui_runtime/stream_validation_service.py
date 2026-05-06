"""
MODULE: stream_validation_service
PURPOSE: Validate AG-UI event stream payloads (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_EVENT_TYPES = {
    "RUN_STARTED",
    "RUN_FINISHED",
    "TOOL_CALL",
    "TOOL_RESULT",
    "CONTEXT_EXPANDED",
    "APPROVAL_REQUIRED",
    "APPROVAL_GRANTED",
    "APPROVAL_DENIED",
    "RETRIEVAL_STARTED",
    "RETRIEVAL_FINISHED",
}


def validate_event(event: dict[str, Any]) -> None:
    if event.get("event_type") not in ALLOWED_EVENT_TYPES:
        raise ValueError("invalid event_type")
    lineage = event.get("workflow_lineage")
    if not isinstance(lineage, dict) or not lineage.get("workflow_id") or not lineage.get("sequence"):
        raise ValueError("workflow lineage required")
    if event.get("hidden_execution") is True:
        raise ValueError("hidden execution rejected")
    if event.get("unrestricted_live_execution") is True:
        raise ValueError("unrestricted live execution rejected")

