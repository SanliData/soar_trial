"""
MODULE: context_partition_service
PURPOSE: Deterministic operational context partitions (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_PARTITIONS: list[dict[str, Any]] = [
    {
        "partition_id": "procurement_documents",
        "description": "Vendor PDFs, bid tables, and catalog snippets.",
        "max_estimated_tokens": 18000,
        "load_order": 2,
    },
    {
        "partition_id": "contractor_history",
        "description": "Credential events, reviews, and permit links.",
        "max_estimated_tokens": 12000,
        "load_order": 1,
    },
    {
        "partition_id": "municipality_notes",
        "description": "Ordinances and bulletin references.",
        "max_estimated_tokens": 8000,
        "load_order": 3,
    },
    {
        "partition_id": "graph_relationships",
        "description": "Serialized read-only graph neighborhood summaries.",
        "max_estimated_tokens": 6000,
        "load_order": 4,
    },
    {
        "partition_id": "workflow_memory",
        "description": "Checkpointed workflow phase summaries.",
        "max_estimated_tokens": 4000,
        "load_order": 0,
    },
]


def export_context_partition_manifest() -> dict[str, Any]:
    ordered = sorted(_PARTITIONS, key=lambda p: p["load_order"])
    return {
        "partitions": [dict(p) for p in ordered],
        "explainable_partition_metadata": True,
        "deterministic": True,
    }
