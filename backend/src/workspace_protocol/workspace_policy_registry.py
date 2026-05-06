"""
MODULE: workspace_policy_registry
PURPOSE: Static workspace governance policies — explicit boundaries only (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

WORKSPACE_POLICY_EPOCH = "2025-05-01T00:00:00Z"

WORKSPACE_POLICIES: dict[str, dict[str, Any]] = {
    "procurement_workspace": {
        "policy_name": "procurement_workspace",
        "workspace_scope": "procurement_sales",
        "execution_permissions": ["read_catalog", "rank_vendors", "draft_summary"],
        "memory_scope": "session_and_project_bounded",
        "escalation_requirements": ["human_above_spend_threshold"],
        "audit_required": True,
        "created_at": WORKSPACE_POLICY_EPOCH,
    },
    "onboarding_workspace": {
        "policy_name": "onboarding_workspace",
        "workspace_scope": "customer_onboarding",
        "execution_permissions": ["draft_checklists", "validate_inputs", "export_pack"],
        "memory_scope": "ephemeral_workspace_buffer",
        "escalation_requirements": ["human_on_pii_ambiguity"],
        "audit_required": True,
        "created_at": WORKSPACE_POLICY_EPOCH,
    },
    "graph_analysis_workspace": {
        "policy_name": "graph_analysis_workspace",
        "workspace_scope": "intel_graph_read",
        "execution_permissions": ["query_graph_projections", "summarize_paths"],
        "memory_scope": "scoped_graph_context_window",
        "escalation_requirements": ["human_on_sensitive_vertex"],
        "audit_required": True,
        "created_at": WORKSPACE_POLICY_EPOCH,
    },
    "executive_reporting_workspace": {
        "policy_name": "executive_reporting_workspace",
        "workspace_scope": "executive_brief",
        "execution_permissions": ["assemble_brief_sections", "cite_sources_only"],
        "memory_scope": "rolling_summary_strict_ttl",
        "escalation_requirements": ["human_signoff_publish"],
        "audit_required": True,
        "created_at": WORKSPACE_POLICY_EPOCH,
    },
}


def export_workspace_policies_manifest() -> list[dict[str, Any]]:
    return [dict(WORKSPACE_POLICIES[k]) for k in sorted(WORKSPACE_POLICIES.keys())]


def get_workspace_policy(policy_name: str) -> dict[str, Any] | None:
    key = policy_name.strip()
    if key not in WORKSPACE_POLICIES:
        return None
    return dict(WORKSPACE_POLICIES[key])
