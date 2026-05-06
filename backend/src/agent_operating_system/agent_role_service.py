"""
MODULE: agent_role_service
PURPOSE: Role-scoped agent capabilities (least privilege) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ROLE_EPOCH = "2026-01-01T00:00:00Z"

AGENT_ROLES: dict[str, dict[str, Any]] = {
    "procurement_reviewer": {
        "role_id": "procurement_reviewer",
        "description": "Read-only procurement analysis and vendor briefings.",
        "allowed_capabilities": ["context.types", "context.lifecycle", "documents.ocr_pipeline"],
        "escalation_policy": "human_on_external_submit_or_export",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "contractor_researcher": {
        "role_id": "contractor_researcher",
        "description": "Contractor profile research with lineage requirements.",
        "allowed_capabilities": ["context.relevance", "documents.layout"],
        "escalation_policy": "human_on_identity_or_license_risk",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "permit_monitor": {
        "role_id": "permit_monitor",
        "description": "Permit monitoring metadata and retrieval sync warnings.",
        "allowed_capabilities": ["context.lifecycle"],
        "escalation_policy": "human_on_external_submission",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "onboarding_specialist": {
        "role_id": "onboarding_specialist",
        "description": "Onboarding checklist generation (metadata only).",
        "allowed_capabilities": ["context.types", "context.compression"],
        "escalation_policy": "human_on_pii_signal",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "executive_reporter": {
        "role_id": "executive_reporter",
        "description": "Executive reporting with deterministic summarization.",
        "allowed_capabilities": ["context.lifecycle"],
        "escalation_policy": "human_on_sensitive_export",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "graph_investigator": {
        "role_id": "graph_investigator",
        "description": "Read-only graph investigation; no graph rewrite.",
        "allowed_capabilities": ["context.isolation"],
        "escalation_policy": "human_on_sensitive_vertex",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
    "compliance_reviewer": {
        "role_id": "compliance_reviewer",
        "description": "Compliance review for command risk and permissions.",
        "allowed_capabilities": ["mcp.tools", "mcp.gateway"],
        "escalation_policy": "human_on_capability_escalation",
        "least_privilege": True,
        "created_at": ROLE_EPOCH,
    },
}


def export_agent_roles() -> dict[str, Any]:
    return {
        "roles": [dict(AGENT_ROLES[k]) for k in sorted(AGENT_ROLES.keys())],
        "role_count": len(AGENT_ROLES),
        "deterministic": True,
        "no_hidden_permissions": True,
    }


def get_role(role_id: str) -> dict[str, Any]:
    key = (role_id or "").strip()
    if key not in AGENT_ROLES:
        raise ValueError("unknown role")
    return dict(AGENT_ROLES[key])

