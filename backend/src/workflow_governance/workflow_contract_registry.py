"""
MODULE: workflow_contract_registry
PURPOSE: Static workflow contract catalog — no runtime mutation (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

***REMOVED*** Fixed creation timestamp for deterministic exports (foundation contracts are versioned, not "now").
CONTRACT_EPOCH = "2025-05-01T00:00:00Z"

WORKFLOW_CONTRACTS: dict[str, dict[str, Any]] = {
    "procurement_analysis": {
        "workflow_name": "procurement_analysis",
        "objective": "Structured vendor and requirement alignment with auditable sourcing rationale.",
        "constraints": ["no_auto_commit_spend", "human_review_above_threshold"],
        "acceptance_criteria": ["requirements_matrix_present", "risk_notes_present", "next_steps_explicit"],
        "recommended_effort": "high",
        "allowed_tools": ["read:crm", "read:graph", "execute:scorecard"],
        "escalation_policy": "threshold_or_ambiguity",
        "output_contract": "artifact_json_v1",
        "created_at": CONTRACT_EPOCH,
    },
    "onboarding_generation": {
        "workflow_name": "onboarding_generation",
        "objective": "Generate tenant-scoped onboarding plans with clear milestones and owners.",
        "constraints": ["pii_minimization", "step_count_cap_12"],
        "acceptance_criteria": ["milestone_list", "owner_fields", "rollback_path"],
        "recommended_effort": "high",
        "allowed_tools": ["read:tenant_profile", "execute:plan_draft"],
        "escalation_policy": "compliance_or_missing_data",
        "output_contract": "onboarding_plan_v1",
        "created_at": CONTRACT_EPOCH,
    },
    "graph_investigation": {
        "workflow_name": "graph_investigation",
        "objective": "Trace company and contact relationships with explainable graph steps.",
        "constraints": ["read_only_graph", "max_hops_5"],
        "acceptance_criteria": ["path_summary", "evidence_citations", "stopping_rule_documented"],
        "recommended_effort": "xhigh",
        "allowed_tools": ["read:graph", "read:entity_cache"],
        "escalation_policy": "data_incompleteness",
        "output_contract": "graph_brief_v1",
        "created_at": CONTRACT_EPOCH,
    },
    "executive_briefing": {
        "workflow_name": "executive_briefing",
        "objective": "Condense multi-source intelligence into an executive-grade brief with clear decisions.",
        "constraints": ["source_attribution", "no_unverified_claims_as_facts"],
        "acceptance_criteria": ["decision_block", "risk_register", "assumptions_explicit"],
        "recommended_effort": "max",
        "allowed_tools": ["read:intel", "read:graph", "execute:summarize"],
        "escalation_policy": "legal_or_reputational",
        "output_contract": "exec_brief_v1",
        "created_at": CONTRACT_EPOCH,
    },
    "opportunity_ranking": {
        "workflow_name": "opportunity_ranking",
        "objective": "Rank opportunities using explicit scoring and tie-breakers.",
        "constraints": ["scoring_transparency", "no_hidden_weights"],
        "acceptance_criteria": ["ranked_list", "score_breakdown", "exclusion_rules"],
        "recommended_effort": "medium",
        "allowed_tools": ["read:opportunities", "execute:rank"],
        "escalation_policy": "data_drift",
        "output_contract": "ranking_table_v1",
        "created_at": CONTRACT_EPOCH,
    },
}


def export_contracts_manifest() -> dict[str, Any]:
    return {
        "contracts": dict(sorted((k, v) for k, v in WORKFLOW_CONTRACTS.items())),
        "contract_count": len(WORKFLOW_CONTRACTS),
        "mutation_policy": "static_registry_only",
    }
