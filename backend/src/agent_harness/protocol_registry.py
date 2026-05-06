"""
MODULE: protocol_registry
PURPOSE: Communication protocol boundaries — explicit trust rules (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

PROTOCOL_TYPES: frozenset[str] = frozenset(
    {
        "agent_to_user",
        "agent_to_tool",
        "agent_to_agent",
        "evaluation_protocol",
        "escalation_protocol",
    }
)

PROTOCOL_REGISTRY: dict[str, dict[str, Any]] = {
    "agent_to_user": {
        "envelope": "structured_json",
        "trust_boundary": "high",
        "requires_audit_trace": True,
    },
    "agent_to_tool": {
        "envelope": "capability_bound_request",
        "trust_boundary": "medium",
        "requires_audit_trace": True,
    },
    "agent_to_agent": {
        "envelope": "delegation_manifest_only",
        "trust_boundary": "medium",
        "requires_audit_trace": True,
        "note": "explicit delegation edges only — no hidden hops",
    },
    "evaluation_protocol": {
        "envelope": "evaluation_route_token",
        "trust_boundary": "high",
        "requires_audit_trace": True,
    },
    "escalation_protocol": {
        "envelope": "human_approval_ticket",
        "trust_boundary": "high",
        "requires_audit_trace": True,
    },
}


def export_protocols_manifest() -> dict[str, Any]:
    keys = sorted(PROTOCOL_REGISTRY.keys())
    return {
        "protocol_types": sorted(PROTOCOL_TYPES),
        "protocols": [{"protocol_id": k, **PROTOCOL_REGISTRY[k]} for k in keys],
    }


def get_protocol(protocol_id: str) -> dict[str, Any] | None:
    if protocol_id not in PROTOCOL_REGISTRY:
        return None
    return {"protocol_id": protocol_id, **PROTOCOL_REGISTRY[protocol_id]}
