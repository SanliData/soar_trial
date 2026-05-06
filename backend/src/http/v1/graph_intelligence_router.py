"""
ROUTER: graph_intelligence_router
PURPOSE: HTTP facade for hybrid graph intelligence (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.graph_intelligence.graph_cache_service import export_graph_cache_manifest
from src.graph_intelligence.graph_projection_service import export_graph_projection_manifest
from src.graph_intelligence.graph_reasoning_service import export_graph_reasoning_manifest
from src.graph_intelligence.hybrid_query_service import export_hybrid_query_plan_manifest
from src.graph_intelligence.relationship_traversal_service import export_relationship_traversal_manifest

router = APIRouter(tags=["graph-intelligence"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "graph_intelligence_foundation": True,
        "autonomous_graph_mutation": False,
        "mandatory_native_graph_db": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/graph/traversals")
async def get_graph_traversals() -> Dict[str, Any]:
    return _envelope(
        {
            "traversals": export_relationship_traversal_manifest(),
            "projections": export_graph_projection_manifest(),
            "graph_cache": export_graph_cache_manifest(),
            "graph_reasoning": export_graph_reasoning_manifest(),
        }
    )


@router.get("/system/graph/hybrid-query")
async def get_hybrid_query() -> Dict[str, Any]:
    return _envelope({"hybrid_query": export_hybrid_query_plan_manifest()})
