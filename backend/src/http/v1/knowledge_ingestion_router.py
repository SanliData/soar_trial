"""
ROUTER: knowledge_ingestion_router
PURPOSE: HTTP facade for structured knowledge ingestion (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from src.knowledge_ingestion.knowledge_block_schema import CreateKnowledgeBlockRequest
from src.knowledge_ingestion.knowledge_ingestion_service import (
    ingest_block,
    list_blocks_response,
    policies_response,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/knowledge", tags=["knowledge-ingestion"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"deterministic_ingestion": True, "scraping_executed": False}
    out.update(payload)
    return out


@router.post("/block")
async def post_knowledge_block(body: CreateKnowledgeBlockRequest) -> Dict[str, Any]:
    try:
        block = ingest_block(body)
        return _envelope({"block": block.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("knowledge block rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/blocks")
async def get_knowledge_blocks(
    limit: int = Query(50, ge=1, le=500),
    geographic_scope: Optional[str] = None,
    industry: Optional[str] = None,
) -> Dict[str, Any]:
    payload = list_blocks_response(limit=limit, geographic_scope=geographic_scope, industry=industry)
    return _envelope(payload)


@router.get("/policies")
async def get_retrieval_policies() -> Dict[str, Any]:
    return _envelope({"policies": policies_response()})
