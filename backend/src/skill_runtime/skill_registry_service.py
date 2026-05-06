"""
MODULE: skill_registry_service
PURPOSE: Deterministic operational skill registry (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

SKILL_REGISTRY_EPOCH = "2025-05-01T00:00:00Z"

SKILL_REGISTRY: dict[str, dict[str, Any]] = {
    "procurement_review": {
        "skill_name": "procurement_review",
        "description": "Rank and brief procurement-aligned vendors with citations.",
        "allowed_tools": ["read_catalog", "structured_summarize"],
        "activation_rules": ["explicit_command", "workflow_trigger"],
        "runtime_scope": "procurement_workspace",
        "escalation_policy": "human_above_threshold_spend",
        "dependency_skills": [],
        "created_at": SKILL_REGISTRY_EPOCH,
        "estimated_token_cost": 4200,
        "prefill_weight": 0.35,
        "cache_eligibility": True,
        "batching_eligibility": True,
        "runtime_efficiency_score": 0.78,
        "context_weight": 0.42,
        "partition_priority": "procurement_documents",
        "retrieval_fallback_allowed": True,
        "sparse_reasoning_compatible": True,
        # H-044 typed context integration (optional fields)
        "required_context_types": ["instruction_context", "knowledge_context", "tool_context", "guardrail_context"],
        "forbidden_context_types": [],
        "context_scope": "workflow_scoped",
        "compression_allowed": True,
        "isolation_required": True,
    },
    "onboarding_validator": {
        "skill_name": "onboarding_validator",
        "description": "Validate onboarding pack completeness and policy alignment.",
        "allowed_tools": ["validate_inputs", "draft_checklists"],
        "activation_rules": ["explicit_command", "evaluation_trigger"],
        "runtime_scope": "onboarding_workspace",
        "escalation_policy": "human_on_pii_signal",
        "dependency_skills": [],
        "created_at": SKILL_REGISTRY_EPOCH,
        "estimated_token_cost": 2800,
        "prefill_weight": 0.28,
        "cache_eligibility": True,
        "batching_eligibility": False,
        "runtime_efficiency_score": 0.81,
        "context_weight": 0.35,
        "partition_priority": "workflow_memory",
        "retrieval_fallback_allowed": True,
        "sparse_reasoning_compatible": False,
        "required_context_types": ["instruction_context", "memory_context", "tool_context", "guardrail_context"],
        "forbidden_context_types": [],
        "context_scope": "workflow_scoped",
        "compression_allowed": True,
        "isolation_required": True,
    },
    "graph_investigator": {
        "skill_name": "graph_investigator",
        "description": "Read-only graph path explanation and summaries.",
        "allowed_tools": ["query_graph_projections", "path_summarize"],
        "activation_rules": ["workflow_trigger", "explicit_command"],
        "runtime_scope": "graph_analysis_workspace",
        "escalation_policy": "human_on_sensitive_vertex",
        "dependency_skills": ["reliability_audit"],
        "created_at": SKILL_REGISTRY_EPOCH,
        "estimated_token_cost": 9600,
        "prefill_weight": 0.52,
        "cache_eligibility": True,
        "batching_eligibility": True,
        "runtime_efficiency_score": 0.72,
        "context_weight": 0.62,
        "partition_priority": "graph_relationships",
        "retrieval_fallback_allowed": True,
        "sparse_reasoning_compatible": True,
        "required_context_types": ["instruction_context", "knowledge_context", "tool_context", "guardrail_context"],
        "forbidden_context_types": [],
        "context_scope": "workflow_scoped",
        "compression_allowed": True,
        "isolation_required": True,
    },
    "reliability_audit": {
        "skill_name": "reliability_audit",
        "description": "Static reliability checklist against governed traces.",
        "allowed_tools": ["read_reliability_manifest"],
        "activation_rules": ["evaluation_trigger", "explicit_command"],
        "runtime_scope": "graph_analysis_workspace",
        "escalation_policy": "notify_on_fail_closed",
        "dependency_skills": [],
        "created_at": SKILL_REGISTRY_EPOCH,
        "estimated_token_cost": 1500,
        "prefill_weight": 0.18,
        "cache_eligibility": True,
        "batching_eligibility": False,
        "runtime_efficiency_score": 0.88,
        "context_weight": 0.22,
        "partition_priority": "workflow_memory",
        "retrieval_fallback_allowed": False,
        "sparse_reasoning_compatible": False,
        "required_context_types": ["instruction_context", "tool_context", "guardrail_context"],
        "forbidden_context_types": ["memory_context"],
        "context_scope": "workflow_scoped",
        "compression_allowed": True,
        "isolation_required": True,
    },
    "browser_compliance": {
        "skill_name": "browser_compliance",
        "description": "Validate browser-session plans against firewall allowlists.",
        "allowed_tools": ["read_firewall_policies"],
        "activation_rules": ["explicit_command"],
        "runtime_scope": "browser_orchestration_proxy",
        "escalation_policy": "human_before_navigate_uncatalogued",
        "dependency_skills": ["onboarding_validator"],
        "created_at": SKILL_REGISTRY_EPOCH,
        "estimated_token_cost": 2200,
        "prefill_weight": 0.22,
        "cache_eligibility": False,
        "batching_eligibility": False,
        "runtime_efficiency_score": 0.84,
        "context_weight": 0.28,
        "partition_priority": "municipality_notes",
        "retrieval_fallback_allowed": True,
        "sparse_reasoning_compatible": False,
        "required_context_types": ["instruction_context", "tool_context", "guardrail_context"],
        "forbidden_context_types": [],
        "context_scope": "workflow_scoped",
        "compression_allowed": True,
        "isolation_required": True,
    },
}


def export_skill_registry_manifest() -> list[dict[str, Any]]:
    return [dict(SKILL_REGISTRY[k]) for k in sorted(SKILL_REGISTRY.keys())]


def get_skill_definition(skill_name: str) -> dict[str, Any] | None:
    key = skill_name.strip()
    if key not in SKILL_REGISTRY:
        return None
    return dict(SKILL_REGISTRY[key])
