"""
ROUTER: semantic_capability_graph_router
PURPOSE: HTTP facade for semantic capability graph (H-034)
NOTE: H-020 owns GET /system/capabilities — graph routes live under /system/capabilities/*
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.semantic_capability_graph.capability_context_service import export_runtime_semantic_snapshot
from src.semantic_capability_graph.capability_graph_registry import export_entity_registry
from src.semantic_capability_graph.capability_topology_service import (
    get_capability_graph,
    list_dependency_paths,
    list_trust_paths,
    summarize_topology,
)
from src.semantic_capability_graph.cross_capability_awareness_service import export_awareness_summaries
from src.semantic_capability_graph.semantic_contract_service import export_contracts

router = APIRouter(prefix="/system/capabilities", tags=["semantic-capability-graph"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "semantic_capability_graph_foundation": True,
        "recursive_capability_mutation": False,
        "autonomous_capability_discovery": False,
        "distributed_semantic_mesh": False,
    }
    merged.update(payload)
    return merged


@router.get("/graph")
async def get_semantic_graph_registry() -> Dict[str, Any]:
    return _envelope({"registry": export_entity_registry()})


@router.get("/topology")
async def get_topology() -> Dict[str, Any]:
    return _envelope(
        {
            "graph": get_capability_graph(),
            "summary": summarize_topology(),
            "dependency_paths": list_dependency_paths("workflow_governance"),
            "trust_paths": list_trust_paths("agent_security"),
        }
    )


@router.get("/contracts")
async def get_contracts() -> Dict[str, Any]:
    return _envelope({"contracts": export_contracts()})


@router.get("/awareness")
async def get_awareness() -> Dict[str, Any]:
    return _envelope({"awareness": export_awareness_summaries()})


@router.get("/runtime-context")
async def get_runtime_context_snapshot() -> Dict[str, Any]:
    return _envelope({"runtime_semantic_snapshot": export_runtime_semantic_snapshot()})
