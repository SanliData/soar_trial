"""
MODULE: semantic_contract_service
PURPOSE: Static cross-capability interaction contracts (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

SEMANTIC_CONTRACTS: tuple[dict[str, Any], ...] = (
    {
        "contract_id": "sc_runtime_to_workflow_v1",
        "source_capability": "runtime_context",
        "target_capability": "workflow_governance",
        "allowed_actions": ["read_metadata_snapshot", "read_topology_hint"],
        "trust_requirements": ["orchestration_safe", "non_destructive"],
        "escalation_policy": "human_review_on_ambiguity",
        "runtime_visibility": "operator_visible",
    },
    {
        "contract_id": "sc_workflow_to_security_v1",
        "source_capability": "workflow_governance",
        "target_capability": "agent_security",
        "allowed_actions": ["policy_check", "capability_isolation_query"],
        "trust_requirements": ["explicit_session", "audit_log"],
        "escalation_policy": "block_on_trust_failure",
        "runtime_visibility": "audit_visible",
    },
    {
        "contract_id": "sc_graph_to_eval_v1",
        "source_capability": "graph_intelligence",
        "target_capability": "trajectory_evaluation",
        "allowed_actions": ["submit_trace_bundle", "read_eval_manifest"],
        "trust_requirements": ["evaluation_enabled", "explainable_outputs"],
        "escalation_policy": "fallback_to_generic_eval",
        "runtime_visibility": "operator_visible",
    },
)


def export_contracts() -> dict[str, Any]:
    return {
        "contracts": list(SEMANTIC_CONTRACTS),
        "contract_count": len(SEMANTIC_CONTRACTS),
        "mutation_policy": "static_contracts_only",
    }


def validate_contract_reference(source: str, target: str) -> None:
    from src.semantic_capability_graph.capability_graph_registry import SEMANTIC_CAPABILITY_ENTITIES

    if source not in SEMANTIC_CAPABILITY_ENTITIES or target not in SEMANTIC_CAPABILITY_ENTITIES:
        raise ValueError("contract reference unknown capability id")
