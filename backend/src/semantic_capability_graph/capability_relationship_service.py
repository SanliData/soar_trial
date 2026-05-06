"""
MODULE: capability_relationship_service
PURPOSE: Deterministic capability edges (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

RELATIONSHIP_TYPES: tuple[str, ...] = (
    "depends_on",
    "trusted_by",
    "evaluated_by",
    "orchestrated_by",
    "secured_by",
    "enriched_by",
)

***REMOVED*** (source_id, relationship_type, target_id) — directed edges.
SEMANTIC_RELATIONSHIPS: tuple[tuple[str, str, str], ...] = (
    ("workflow_governance", "depends_on", "runtime_context"),
    ("workflow_governance", "secured_by", "agent_security"),
    ("graph_intelligence", "evaluated_by", "trajectory_evaluation"),
    ("trajectory_evaluation", "depends_on", "runtime_context"),
    ("reliability_governance", "depends_on", "runtime_context"),
    ("graph_intelligence", "enriched_by", "workflow_governance"),
    ("agent_security", "trusted_by", "workflow_governance"),
    ***REMOVED*** H-045 relationships
    ("agent_os", "depends_on", "workspace_protocol"),
    ("federated_retrieval", "enriched_by", "knowledge_ingestion"),
    ("selective_context_runtime", "depends_on", "inference_runtime"),
    ("nl_control_plane", "secured_by", "agent_proxy_firewall"),
)


def export_relationships() -> dict[str, Any]:
    edges = [
        {"source": s, "relationship": r, "target": t} for s, r, t in SEMANTIC_RELATIONSHIPS
    ]
    return {
        "relationship_types": list(RELATIONSHIP_TYPES),
        "edges": edges,
        "edge_count": len(edges),
    }

