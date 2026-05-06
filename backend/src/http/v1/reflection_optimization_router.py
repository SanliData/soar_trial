"""
ROUTER: reflection_optimization_router
PURPOSE: Reflection trace & prompt candidate HTTP facade (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query

from src.reflection_optimization.prompt_candidate_registry import (
    approve_candidate,
    create_candidate_from_trace_id,
    list_candidates,
    reject_candidate,
)
from src.reflection_optimization.reflection_schema import (
    ApproveCandidateBody,
    CreateCandidateFromTraceRequest,
    CreateTraceRequest,
    RejectCandidateBody,
)
from src.reflection_optimization.reflection_trace_service import (
    record_trace,
    list_traces_filtered,
)
from src.reflection_optimization.reflection_validation_service import validate_trace_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/reflection", tags=["reflection-optimization"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out = {"autonomous_execution": False}
    out.update(payload)
    return out


@router.post("/trace")
async def post_trace(body: CreateTraceRequest) -> Dict[str, Any]:
    try:
        validate_trace_request(body)
        trace = record_trace(body)
        return _envelope({"trace": trace.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("reflection trace rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/candidate")
async def post_candidate(body: CreateCandidateFromTraceRequest) -> Dict[str, Any]:
    try:
        cand = create_candidate_from_trace_id(
            body.trace_id,
            workflow_override=body.workflow_name,
        )
        return _envelope({"candidate": cand.model_dump(mode="json")})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/traces")
async def get_traces(
    limit: int = Query(50, ge=1, le=500),
    workflow: Optional[str] = None,
    failed_only: bool = Query(False),
) -> Dict[str, Any]:
    rows = list_traces_filtered(limit=limit, workflow_name=workflow, failed_only=failed_only)
    return _envelope({"traces": [t.model_dump(mode="json") for t in rows]})


@router.get("/candidates")
async def get_candidates(
    limit: int = Query(50, ge=1, le=500),
    workflow: Optional[str] = None,
) -> Dict[str, Any]:
    rows = list_candidates(limit=limit, workflow_name=workflow)
    return _envelope({"candidates": [c.model_dump(mode="json") for c in rows]})


@router.post("/candidate/{candidate_id}/approve")
async def post_approve(candidate_id: str, body: ApproveCandidateBody) -> Dict[str, Any]:
    try:
        cand = approve_candidate(
            candidate_id,
            approved_by=body.approved_by.strip(),
            evaluation_notes=body.evaluation_notes,
        )
        return _envelope({"candidate": cand.model_dump(mode="json")})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/candidate/{candidate_id}/reject")
async def post_reject(candidate_id: str, body: RejectCandidateBody) -> Dict[str, Any]:
    try:
        cand = reject_candidate(
            candidate_id,
            rejected_by=body.rejected_by.strip(),
            evaluation_notes=body.evaluation_notes,
        )
        return _envelope({"candidate": cand.model_dump(mode="json")})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
