"""
MODULE: hybrid_query_service
PURPOSE: Relational-first plans with optional graph augmentation (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_hybrid_query_plan_manifest() -> dict[str, Any]:
    return {
        "plans": [
            {
                "query_id": "hq-contractors-by-tier",
                "relational_steps": ["filter_contractors", "sort_by_updated_at"],
                "graph_augment_optional": ["expand_neighbor_utilities_depth2"],
                "mandatory_graph_dependency": False,
            },
            {
                "query_id": "hq-permits-with-blockers",
                "relational_steps": ["join_permits_projects"],
                "graph_augment_optional": ["trace_dependency_chain_depth3"],
                "mandatory_graph_dependency": False,
            },
        ],
        "relational_authoritative_for_acid_fields": True,
        "deterministic": True,
    }
