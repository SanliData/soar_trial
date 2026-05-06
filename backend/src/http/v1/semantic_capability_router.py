"""
ROUTER: semantic_capability_router
PURPOSE: Public semantic capability manifest for planners (H-020)
ENCODING: UTF-8 WITHOUT BOM

Router stays limited to invoking the deterministic export service — no branching business rules.
"""

import logging

from fastapi import APIRouter, HTTPException

from src.semantic_capabilities.capability_export_service import build_capabilities_catalog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["semantic-capabilities"])


@router.get("/capabilities")
async def get_semantic_capabilities() -> dict:
    try:
        return build_capabilities_catalog()
    except Exception as exc:
        logger.exception("semantic_capabilities_export_failed")
        raise HTTPException(status_code=500, detail="capabilities_unavailable") from exc
