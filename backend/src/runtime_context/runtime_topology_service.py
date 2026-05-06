"""
MODULE: runtime_topology_service
PURPOSE: Structured topology visibility — curated manifest only (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

# Curated topology — no arbitrary sys.modules or socket scans.
_TOPOLOGY: dict[str, Any] = {
    "active_routers": sorted(
        [
            "v1_router",
            "semantic_capability_router",
            "commercial_graph_router",
            "knowledge_ingestion_router",
            "intelligence_widget_router",
            "prompt_orchestration_router",
            "trajectory_evaluation_router",
            "agent_security_router",
            "runtime_context_router",
            "context_orchestration_router",
            "context_compression_router",
            "context_isolation_router",
            "document_intelligence_router",
            "mcp_runtime_router",
            "agent_operating_system_router",
            "natural_language_control_plane_router",
            "federated_retrieval_router",
            "selective_context_runtime_router",
        ]
    ),
    "active_domains": sorted(
        [
            "semantic_capabilities",
            "commercial_graph",
            "knowledge",
            "widgets",
            "prompts",
            "trajectory",
            "security",
            "runtime",
            "context_orchestration",
            "context_compression",
            "context_isolation",
            "document_intelligence",
            "mcp_runtime",
            "agent_os",
            "nl_control_plane",
            "federated_retrieval",
            "selective_context_runtime",
        ]
    ),
    "enabled_integrations": sorted(["results_export", "graph_traversal", "widget_render"]),
    "graph_availability": True,
    "ingestion_pipelines": sorted(["knowledge_ingest_v1"]),
}


def build_topology_snapshot() -> dict[str, Any]:
    return dict(_TOPOLOGY)
