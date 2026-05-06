"""
ROUTER: commercial_graph_router
PURPOSE: HTTP facade for commercial graph intelligence (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from src.commercial_graph.commercial_graph_builder import (
    create_entity,
    create_relationship,
    get_entity,
    list_relationships,
)
from src.commercial_graph.entity_schema import (
    CreateCommercialEntityRequest,
    CreateCommercialRelationshipRequest,
)
from src.commercial_graph.graph_traversal_service import traverse_payload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/graph", tags=["commercial-graph"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"deterministic_graph": True, "graph_db_required": False}
    out.update(payload)
    return out


@router.post("/entity")
async def post_entity(body: CreateCommercialEntityRequest) -> Dict[str, Any]:
    try:
        ent = create_entity(body)
        return _envelope({"entity": ent.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("commercial entity rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/relationship")
async def post_relationship(body: CreateCommercialRelationshipRequest) -> Dict[str, Any]:
    try:
        rel = create_relationship(body)
        return _envelope({"relationship": rel.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("commercial relationship rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/entity/{entity_id}")
async def get_entity_detail(entity_id: str) -> Dict[str, Any]:
    ent = get_entity(entity_id)
    if not ent:
        raise HTTPException(status_code=404, detail="entity not found")
    return _envelope({"entity": ent.model_dump(mode="json")})


@router.get("/relationships")
async def get_relationships(
    source_entity_id: Optional[str] = None,
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0),
) -> Dict[str, Any]:
    rows = list_relationships(source_entity_id=source_entity_id, min_confidence=min_confidence)
    return _envelope({"relationships": [r.model_dump(mode="json") for r in rows]})


@router.get("/traverse")
async def get_traverse(
    entity_id: str = Query(..., min_length=1),
    depth: int = Query(2, ge=1, le=10),
    relationship_type: Optional[str] = None,
    include_opportunities: bool = Query(False),
    path_to: Optional[str] = None,
) -> Dict[str, Any]:
    try:
        payload = traverse_payload(
            entity_id,
            depth=depth,
            relationship_type=relationship_type,
            include_opportunities=include_opportunities,
            path_to=path_to,
        )
        return _envelope(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
