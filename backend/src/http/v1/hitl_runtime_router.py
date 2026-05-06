"""
ROUTER: hitl_runtime_router
PURPOSE: HITL runtime governance facade (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.hitl_runtime.approval_checkpoint_service import export_checkpoints
from src.hitl_runtime.escalation_policy_service import export_escalations
from src.hitl_runtime.human_review_queue import export_review_queue

router = APIRouter(prefix="/system/hitl", tags=["hitl-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "hitl_runtime_foundation": True,
        "no_automatic_approval": True,
        "approval_lineage_mandatory": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/checkpoints")
async def get_checkpoints() -> Dict[str, Any]:
    return _envelope(export_checkpoints())


@router.get("/review-queue")
async def get_review_queue() -> Dict[str, Any]:
    return _envelope(export_review_queue(limit=25))


@router.get("/escalations")
async def get_escalations() -> Dict[str, Any]:
    return _envelope(export_escalations())

