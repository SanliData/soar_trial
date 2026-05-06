"""
MODULE: capability_graph_registry
PURPOSE: Static semantic capability entities — no runtime mutation (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

GRAPH_EPOCH = "2025-05-01T00:00:00Z"

SEMANTIC_CAPABILITY_ENTITIES: dict[str, dict[str, Any]] = {
    "runtime_context": {
        "capability_name": "runtime_context",
        "capability_type": "runtime_metadata",
        "orchestration_safe": True,
        "trust_level": "medium",
        "graph_access": "read_only",
        "evaluation_enabled": False,
        "runtime_visible": True,
        "related_capabilities": ["workflow_governance", "reliability_governance"],
        "created_at": GRAPH_EPOCH,
    },
    "workflow_governance": {
        "capability_name": "workflow_governance",
        "capability_type": "workflow_policy",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["runtime_context", "trajectory_evaluation", "agent_security"],
        "created_at": GRAPH_EPOCH,
    },
    "trajectory_evaluation": {
        "capability_name": "trajectory_evaluation",
        "capability_type": "evaluation",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_write_trace",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["workflow_governance", "graph_intelligence"],
        "created_at": GRAPH_EPOCH,
    },
    "graph_intelligence": {
        "capability_name": "graph_intelligence",
        "capability_type": "graph_reasoning",
        "orchestration_safe": True,
        "trust_level": "medium",
        "graph_access": "graph_query",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["trajectory_evaluation", "agent_security", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "reliability_governance": {
        "capability_name": "reliability_governance",
        "capability_type": "reliability",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["workflow_governance", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "agent_security": {
        "capability_name": "agent_security",
        "capability_type": "security",
        "orchestration_safe": True,
        "trust_level": "critical",
        "graph_access": "policy_gate",
        "evaluation_enabled": False,
        "runtime_visible": True,
        "related_capabilities": ["workflow_governance", "graph_intelligence"],
        "created_at": GRAPH_EPOCH,
    },
    ***REMOVED*** H-045 nodes (governed foundations)
    "agent_os": {
        "capability_name": "agent_os",
        "capability_type": "agent_operations",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["workspace_protocol", "agent_security", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "workspace_protocol": {
        "capability_name": "workspace_protocol",
        "capability_type": "workspace_governance",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["agent_security", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "federated_retrieval": {
        "capability_name": "federated_retrieval",
        "capability_type": "retrieval_fabric",
        "orchestration_safe": True,
        "trust_level": "medium",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["knowledge_ingestion", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "knowledge_ingestion": {
        "capability_name": "knowledge_ingestion",
        "capability_type": "knowledge",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "selective_context_runtime": {
        "capability_name": "selective_context_runtime",
        "capability_type": "context_selective_runtime",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["inference_runtime", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "inference_runtime": {
        "capability_name": "inference_runtime",
        "capability_type": "inference_governance",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
    "nl_control_plane": {
        "capability_name": "nl_control_plane",
        "capability_type": "command_routing",
        "orchestration_safe": True,
        "trust_level": "high",
        "graph_access": "read_only",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["agent_proxy_firewall", "agent_os"],
        "created_at": GRAPH_EPOCH,
    },
    "agent_proxy_firewall": {
        "capability_name": "agent_proxy_firewall",
        "capability_type": "firewall",
        "orchestration_safe": True,
        "trust_level": "critical",
        "graph_access": "policy_gate",
        "evaluation_enabled": True,
        "runtime_visible": True,
        "related_capabilities": ["agent_security", "runtime_context"],
        "created_at": GRAPH_EPOCH,
    },
}


def export_entity_registry() -> dict[str, Any]:
    return {
        "entities": dict(sorted(SEMANTIC_CAPABILITY_ENTITIES.items())),
        "entity_count": len(SEMANTIC_CAPABILITY_ENTITIES),
        "mutation_policy": "static_registry_only",
    }


def get_entity(capability_id: str) -> dict[str, Any]:
    if capability_id not in SEMANTIC_CAPABILITY_ENTITIES:
        raise ValueError(f"unknown semantic capability: {capability_id}")
    return dict(SEMANTIC_CAPABILITY_ENTITIES[capability_id])
