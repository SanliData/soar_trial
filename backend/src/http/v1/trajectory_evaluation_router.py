"""
ROUTER: trajectory_evaluation_router
PURPOSE: HTTP facade for trajectory storage and relative evaluation (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.trajectory_evaluation.evaluation_trace_service import execute_relative_evaluation, list_evaluation_traces
from src.trajectory_evaluation.trajectory_group_service import create_group
from src.trajectory_evaluation.trajectory_registry import create_trajectory, get_trajectory_store
from src.trajectory_evaluation.trajectory_schema import (
    RelativeEvaluateRequest,
    TrajectoryCreateRequest,
    TrajectoryGroupCreateRequest,
)
from src.trajectory_evaluation.trajectory_validation_service import validate_evaluate_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/trajectory", tags=["trajectory-evaluation"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "deterministic_trajectory_evaluation": True,
        "reinforcement_learning_training": False,
        "hidden_reasoning_exposure": "none",
    }
    out.update(payload)
    return out


@router.post("", summary="Create trajectory record")
async def post_trajectory(body: TrajectoryCreateRequest) -> Dict[str, Any]:
    try:
        store = get_trajectory_store()
        traj = create_trajectory(store, body)
        return _envelope({"trajectory": traj.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("trajectory create rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/group")
async def post_group(body: TrajectoryGroupCreateRequest) -> Dict[str, Any]:
    try:
        store = get_trajectory_store()
        group = create_group(store, body)
        return _envelope({"group": group.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("trajectory group rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/evaluate")
async def post_evaluate(body: RelativeEvaluateRequest) -> Dict[str, Any]:
    try:
        store = get_trajectory_store()
        validate_evaluate_request(body, store)
        evaluation = execute_relative_evaluation(store, body.group_id)
        return _envelope({"evaluation": evaluation.model_dump(mode="json")})
    except ValueError as exc:
        logger.info("trajectory evaluate rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/groups")
async def get_groups() -> Dict[str, Any]:
    store = get_trajectory_store()
    groups = [g.model_dump(mode="json") for g in store.list_groups()]
    return _envelope({"groups": groups})


@router.get("/evaluations")
async def get_evaluations() -> Dict[str, Any]:
    store = get_trajectory_store()
    evs = [e.model_dump(mode="json") for e in list_evaluation_traces(store)]
    return _envelope({"evaluations": evs})
