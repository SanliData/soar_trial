"""
MODULE: graph_projection_service
PURPOSE: Read projections over operational entities — hybrid compatible (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_graph_projection_manifest() -> dict[str, Any]:
    return {
        "projections": [
            {
                "projection_id": "proj_contractor_utility_edges",
                "vertex_kinds": ["contractor", "utility", "permit"],
                "edge_kinds": ["serves", "depends_on"],
                "read_only": True,
                "autonomous_graph_mutation": False,
            },
            {
                "projection_id": "proj_subcontractor_chain",
                "vertex_kinds": ["contractor", "subcontractor", "task"],
                "edge_kinds": ["subcontracts_to", "assigned"],
                "read_only": True,
                "autonomous_graph_mutation": False,
            },
        ],
        "mandatory_native_graph_db": False,
        "deterministic": True,
    }
