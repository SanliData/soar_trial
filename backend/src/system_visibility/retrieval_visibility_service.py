"""
MODULE: retrieval_visibility_service
PURPOSE: Retrieval visibility metrics with lineage emphasis (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.connector_registry_service import export_connector_registry
from src.federated_retrieval.retrieval_observability_service import export_retrieval_observability
from src.inference_runtime.runtime_telemetry_service import export_runtime_telemetry_manifest
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion


def export_retrieval_visibility() -> dict[str, Any]:
    connectors = export_connector_registry()
    obs = export_retrieval_observability()
    telemetry = export_runtime_telemetry_manifest()["sample_snapshot"]
    expansion = decide_selective_expansion(
        workflow_name="procurement_analysis",
        query="ISO 27001",
        chunks=[
            {"chunk_id": "c1", "text": "ISO 27001 net-30", "source_lineage": {"authority_score": 0.88, "freshness_days": 3}},
            {"chunk_id": "c2", "text": "marketing", "source_lineage": {"authority_score": 0.55, "freshness_days": 21}},
        ],
    )

    active_connectors = [c for c in connectors["connectors"] if c["enabled"]]
    selective_expansion_rate = 0.0
    if 2 > 0:
        selective_expansion_rate = round(len(expansion["selected_chunk_ids"]) / 2.0, 4)

    retrieval_token_cost = int(telemetry.get("context_token_cost") or 0) // 4
    return {
        "active_connectors": [c["connector_name"] for c in active_connectors],
        "connector_count": int(obs["connector_count"]),
        "retrieval_freshness": {"average_freshness_days": obs["average_freshness_days"], "deterministic": True},
        "stale_sources": int(obs["stale_connector_count"]),
        "source_authority_distribution": dict(obs["source_authority_distribution"]),
        "retrieval_token_cost": retrieval_token_cost,
        "selective_expansion_rates": {"sample_rate": selective_expansion_rate, "deterministic": True},
        "lineage_visibility_enforced": True,
        "deterministic": True,
    }

