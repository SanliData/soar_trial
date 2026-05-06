"""
MODULE: relationship_snapshot_service
PURPOSE: Graph-friendly deterministic relationship snapshots (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_relationships() -> dict[str, Any]:
    nodes = [
        {"node_id": "ctr-001", "type": "contractor", "label": "Sanli Infrastructure Partners"},
        {"node_id": "util-001", "type": "utility", "label": "Example Electric"},
        {"node_id": "mun-001", "type": "municipality", "label": "Example City"},
        {"node_id": "proj-101", "type": "project", "label": "Fiber rollout phase 2"},
    ]
    edges = [
        {"edge_id": "e1", "from": "ctr-001", "to": "util-001", "type": "approved_vendor"},
        {"edge_id": "e2", "from": "ctr-001", "to": "proj-101", "type": "executed"},
        {"edge_id": "e3", "from": "proj-101", "to": "mun-001", "type": "permitted_by"},
    ]
    return {
        "nodes": nodes,
        "edges": edges,
        "procurement_dependencies": [{"depends_on": "permit_validation", "owner": "mun-001"}],
        "deterministic": True,
    }

