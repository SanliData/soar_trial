"""
MODULE: evidence_trace_service
PURPOSE: Evidence lineage and workflow evidence chain (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.federated_search_service import federated_search
from src.results_hub.results_hub_validation_service import require_lineage


def export_evidence_traces(*, query: str = "procurement opportunity") -> dict[str, Any]:
    res = federated_search(query=query, mode="hybrid", limit=6)
    evidence = []
    for r in res["results"]:
        evidence.append(
            {
                "evidence_id": f"ev-{r['record_id']}",
                "title": r["title"],
                "snippet": r["snippet"],
                "connector_origin": r["source_lineage"]["source_name"],
                "workflow_evidence_chain": ["retrieval", "lineage_validation"],
                "context_expansion_source": "selective_context_runtime",
                "source_lineage": r["source_lineage"],
                "deterministic": True,
            }
        )
    require_lineage(evidence)
    return {"query": query, "evidence": evidence, "deterministic": True, "no_orphaned_conclusions": True}

