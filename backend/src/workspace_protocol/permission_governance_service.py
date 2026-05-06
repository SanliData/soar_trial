"""
MODULE: permission_governance_service
PURPOSE: Explicit operational permission manifests — auditable (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_permission_governance_manifest() -> dict[str, Any]:
    return {
        "execution_allowlists": {
            "default_workspace": ["read_catalog", "rank_vendors", "draft_summary", "assemble_brief_sections"],
            "elevated_audit": ["read_catalog", "rank_vendors", "validate_inputs", "query_graph_projections"],
        },
        "deny_rules": [
            {"deny_id": "d-net-001", "pattern": "arbitrary_wide_internet_browser", "effect": "block"},
            {"deny_id": "d-mem-001", "pattern": "unscoped_cross_tenant_memory_write", "effect": "block"},
            {"deny_id": "d-spawn-001", "pattern": "ungoverned_parallel_subagent_fanout", "effect": "block"},
        ],
        "memory_restrictions": [
            "no_raw_secret_storage",
            "ttl_enforced_summaries_only",
            "cross_project_reads_denied_without_grant",
        ],
        "domain_restrictions": ["egress_via_gateway_registry_only"],
        "escalation_requirements": [
            "human_checkout_above_policy_risk",
            "dual_control_on_publish_paths",
        ],
        "hidden_execution_permissions": False,
    }
