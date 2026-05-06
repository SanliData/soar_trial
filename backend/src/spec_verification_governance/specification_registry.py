"""
MODULE: specification_registry
PURPOSE: Static implementation specifications — no runtime mutation (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

SPEC_EPOCH = "2025-05-01T00:00:00Z"

SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "procurement_analysis": {
        "specification_name": "procurement_analysis",
        "objective": "Auditable procurement alignment with explicit sourcing rationale.",
        "constraints": ["human_review_above_threshold", "no_auto_commit"],
        "acceptance_criteria": ["requirements_matrix", "risk_notes", "next_steps"],
        "verification_requirements": ["pytest_module_present", "verify_script_green"],
        "escalation_policy": "threshold_or_ambiguity",
        "architecture_contracts": ["router_no_business_logic", "deterministic_workflows"],
        "created_at": SPEC_EPOCH,
    },
    "onboarding_generation": {
        "specification_name": "onboarding_generation",
        "objective": "Tenant-scoped onboarding plans with milestones and owners.",
        "constraints": ["pii_minimization", "step_cap"],
        "acceptance_criteria": ["milestones", "owners", "rollback_path"],
        "verification_requirements": ["demo_ui_contract", "livebook_section"],
        "escalation_policy": "compliance_missing_data",
        "architecture_contracts": ["no_secrets_in_manifest", "utf8_no_bom"],
        "created_at": SPEC_EPOCH,
    },
    "graph_investigation": {
        "specification_name": "graph_investigation",
        "objective": "Explainable graph traversals with hop limits and citations.",
        "constraints": ["read_only_graph", "max_hops"],
        "acceptance_criteria": ["path_summary", "evidence_citations"],
        "verification_requirements": ["graph_evaluation_route_ok"],
        "escalation_policy": "data_incompleteness",
        "architecture_contracts": ["no_unrestricted_orchestration"],
        "created_at": SPEC_EPOCH,
    },
    "workflow_validation": {
        "specification_name": "workflow_validation",
        "objective": "Workflow outputs satisfy contract acceptance and escalation rules.",
        "constraints": ["delegation_caps", "parallel_limits"],
        "acceptance_criteria": ["contract_keys_present", "constraints_flag_true"],
        "verification_requirements": ["workflow_governance_tests"],
        "escalation_policy": "human_on_acceptance_failure",
        "architecture_contracts": ["router_thin", "services_own_logic"],
        "created_at": SPEC_EPOCH,
    },
    "executive_reporting": {
        "specification_name": "executive_reporting",
        "objective": "Executive-grade briefs with decisions, risks, and explicit assumptions.",
        "constraints": ["source_attribution", "no_unverified_facts"],
        "acceptance_criteria": ["decision_block", "risk_register", "assumptions"],
        "verification_requirements": ["mainbook_proof_section"],
        "escalation_policy": "legal_or_reputational",
        "architecture_contracts": ["auditability_required"],
        "created_at": SPEC_EPOCH,
    },
}


def export_specifications_manifest() -> dict[str, Any]:
    return {
        "specifications": dict(sorted(SPECIFICATIONS.items())),
        "spec_count": len(SPECIFICATIONS),
        "mutation_policy": "static_registry_only",
    }


def get_specification(spec_id: str) -> dict[str, Any]:
    if spec_id not in SPECIFICATIONS:
        raise ValueError(f"unknown specification: {spec_id}")
    return dict(SPECIFICATIONS[spec_id])
