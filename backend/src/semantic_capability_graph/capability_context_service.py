"""
MODULE: capability_context_service
PURPOSE: Runtime semantic snapshots — curated, no blind introspection (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.semantic_capability_graph.capability_graph_registry import SEMANTIC_CAPABILITY_ENTITIES
from src.semantic_capability_graph.capability_topology_service import summarize_topology


def export_runtime_semantic_snapshot() -> dict[str, Any]:
    return {
        "active_capabilities": sorted(SEMANTIC_CAPABILITY_ENTITIES.keys()),
        "trusted_workflows": ["workflow_governance", "trajectory_evaluation"],
        "graph_enabled_domains": ["graph_intelligence"],
        "evaluation_aware": [
            "trajectory_evaluation",
            "reliability_governance",
            "workflow_governance",
            "graph_intelligence",
        ],
        "restricted_capabilities": [],
        "snapshot_rule": "static_curated_v1",
        "unrestricted_introspection": False,
    }


def build_h020_semantic_graph_extension() -> dict[str, Any]:
    """Embedded into H-020 catalog export — deterministic pointer + topology summary."""
    return {
        "schema_version": "h034_v1",
        "integrated_with": "H-020 semantic capability catalog",
        "graph_endpoints": {
            "registry": "/api/v1/system/capabilities/graph",
            "topology": "/api/v1/system/capabilities/topology",
            "contracts": "/api/v1/system/capabilities/contracts",
            "awareness": "/api/v1/system/capabilities/awareness",
            "runtime_snapshot": "/api/v1/system/capabilities/runtime-context",
        },
        "topology_summary": summarize_topology(),
        "recursive_capability_mutation": False,
        "autonomous_capability_discovery": False,
    }
