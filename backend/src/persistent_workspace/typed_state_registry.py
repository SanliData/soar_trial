"""
MODULE: typed_state_registry
PURPOSE: Typed operational state kinds — deterministic schemas (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

STATE_TYPES: tuple[str, ...] = (
    "workflow_state",
    "contractor_state",
    "onboarding_state",
    "graph_state",
    "evaluation_state",
    ***REMOVED*** H-048 additions
    "conversation_session_state",
    "workflow_event_stream_state",
    "approval_lineage_state",
)

***REMOVED*** Canonical field shapes per type (manifest documentation; not DB DDL).
STATE_FIELD_SHAPES: dict[str, list[dict[str, Any]]] = {
    "workflow_state": [
        {"name": "workflow_id", "value_type": "string", "required": True},
        {"name": "phase", "value_type": "enum", "allowed": ["draft", "active", "blocked", "closed"]},
        {"name": "last_checkpoint_at", "value_type": "iso8601", "required": False},
    ],
    "contractor_state": [
        {"name": "contractor_id", "value_type": "string", "required": True},
        {"name": "compliance_tier", "value_type": "enum", "allowed": ["unverified", "verified", "restricted"]},
        {"name": "active_permits", "value_type": "list_ref", "required": False},
    ],
    "onboarding_state": [
        {"name": "tenant_id", "value_type": "string", "required": True},
        {"name": "steps_completed", "value_type": "int", "required": True},
        {"name": "policy_pack_version", "value_type": "string", "required": True},
    ],
    "graph_state": [
        {"name": "projection_id", "value_type": "string", "required": True},
        {"name": "read_only", "value_type": "bool", "required": True},
        {"name": "edge_cursor", "value_type": "string", "required": False},
    ],
    "evaluation_state": [
        {"name": "run_id", "value_type": "string", "required": True},
        {"name": "scorecard_version", "value_type": "string", "required": True},
        {"name": "verdict", "value_type": "enum", "allowed": ["pass", "fail", "review"]},
    ],
    "conversation_session_state": [
        {"name": "session_id", "value_type": "string", "required": True},
        {"name": "workflow_scope", "value_type": "string", "required": True},
        {"name": "conversation_length", "value_type": "int", "required": True},
        {"name": "policy_status", "value_type": "enum", "allowed": ["aligned", "warning", "elevated_risk", "critical"]},
    ],
    "workflow_event_stream_state": [
        {"name": "workflow_id", "value_type": "string", "required": True},
        {"name": "last_event_sequence", "value_type": "int", "required": True},
        {"name": "event_types_seen", "value_type": "list_ref", "required": False},
    ],
    "approval_lineage_state": [
        {"name": "workflow_id", "value_type": "string", "required": True},
        {"name": "checkpoint_id", "value_type": "string", "required": True},
        {"name": "approval_state", "value_type": "enum", "allowed": ["required", "granted", "denied", "escalated"]},
    ],
}


def export_typed_state_registry_manifest() -> dict[str, Any]:
    rows = []
    for st in STATE_TYPES:
        rows.append(
            {
                "state_type": st,
                "fields": list(STATE_FIELD_SHAPES[st]),
                "storage_contract": "typed_storage_only",
                "auditable_transitions": True,
            }
        )
    return {
        "state_types": rows,
        "recursive_self_expanding_memory": False,
        "deterministic": True,
    }
