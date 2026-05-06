"""
MODULE: agent_registry_service
PURPOSE: Deterministic agent registry (no autonomous spawning) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_os_validation_service import validate_agent_record

AGENT_EPOCH = "2026-01-01T00:00:00Z"

AGENT_REGISTRY: dict[str, dict[str, Any]] = {
    "procurement_agent": {
        "agent_id": "procurement_agent",
        "agent_name": "Procurement Agent",
        "agent_role": "procurement_reviewer",
        "workflow_scope": "procurement_analysis",
        "allowed_capabilities": ["context.types", "context.lifecycle", "documents.ocr_pipeline"],
        "permission_scope": "governed_readonly",
        "status": "active",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["procurement", "governed"],
    },
    "contractor_intelligence_agent": {
        "agent_id": "contractor_intelligence_agent",
        "agent_name": "Contractor Intelligence Agent",
        "agent_role": "contractor_researcher",
        "workflow_scope": "contractor_ranking",
        "allowed_capabilities": ["context.relevance", "documents.layout", "documents.markdown_projection"],
        "permission_scope": "governed_readonly",
        "status": "active",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["contractors", "lineage_required"],
    },
    "permit_monitoring_agent": {
        "agent_id": "permit_monitoring_agent",
        "agent_name": "Permit Monitoring Agent",
        "agent_role": "permit_monitor",
        "workflow_scope": "permit_monitoring",
        "allowed_capabilities": ["context.lifecycle"],
        "permission_scope": "governed_readonly",
        "status": "paused",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["permits", "monitoring"],
    },
    "onboarding_agent": {
        "agent_id": "onboarding_agent",
        "agent_name": "Onboarding Agent",
        "agent_role": "onboarding_specialist",
        "workflow_scope": "onboarding_generation",
        "allowed_capabilities": ["context.compression", "context.types"],
        "permission_scope": "governed_readonly",
        "status": "active",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["onboarding"],
    },
    "executive_reporting_agent": {
        "agent_id": "executive_reporting_agent",
        "agent_name": "Executive Reporting Agent",
        "agent_role": "executive_reporter",
        "workflow_scope": "executive_reporting",
        "allowed_capabilities": ["context.lifecycle"],
        "permission_scope": "governed_readonly",
        "status": "active",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["executive"],
    },
    "graph_investigation_agent": {
        "agent_id": "graph_investigation_agent",
        "agent_name": "Graph Investigation Agent",
        "agent_role": "graph_investigator",
        "workflow_scope": "graph_investigation",
        "allowed_capabilities": ["context.isolation"],
        "permission_scope": "governed_readonly",
        "status": "active",
        "human_approval_required": True,
        "created_at": AGENT_EPOCH,
        "tags": ["graph"],
    },
}


def export_agent_registry() -> dict[str, Any]:
    agents = []
    for aid in sorted(AGENT_REGISTRY.keys()):
        row = dict(AGENT_REGISTRY[aid])
        validate_agent_record(row)
        agents.append(row)
    return {
        "agents": agents,
        "agent_count": len(agents),
        "deterministic_registry_only": True,
        "autonomous_spawning": False,
        "no_hidden_permissions": True,
    }


def get_agent(agent_id: str) -> dict[str, Any]:
    key = (agent_id or "").strip()
    if key not in AGENT_REGISTRY:
        raise ValueError("unknown agent")
    row = dict(AGENT_REGISTRY[key])
    validate_agent_record(row)
    return row

