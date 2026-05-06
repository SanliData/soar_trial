"""
MODULE: trajectory_validation_service
PURPOSE: Validate workflow consistency, grouping, and evaluation payloads (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Optional

from src.trajectory_evaluation.trajectory_registry import TrajectoryStore
from src.trajectory_evaluation.trajectory_schema import (
    RelativeEvaluateRequest,
    TrajectoryCreateRequest,
    TrajectoryGroupCreateRequest,
)


def _err(msg: str) -> None:
    raise ValueError(msg)


def validate_create_trajectory(body: TrajectoryCreateRequest) -> None:
    if body.evaluation_score is not None and not (0.0 <= body.evaluation_score <= 100.0):
        _err("evaluation_score must be between 0 and 100 when set")


def validate_group_create(body: TrajectoryGroupCreateRequest, store: TrajectoryStore) -> None:
    if not body.trajectory_ids:
        _err("trajectory_ids must be non-empty for group creation")
    wf: Optional[str] = None
    for tid in body.trajectory_ids:
        t = store.get_trajectory(tid)
        if t is None:
            _err(f"unknown trajectory_id: {tid}")
        if wf is None:
            wf = t.workflow_name
        elif t.workflow_name != wf:
            _err("all trajectories in a group must share the same workflow_name")
        if t.workflow_name != body.workflow_name:
            _err("trajectory workflow does not match group workflow_name")


def validate_evaluate_request(body: RelativeEvaluateRequest, store: TrajectoryStore) -> None:
    g = store.get_group(body.group_id)
    if g is None:
        _err(f"unknown group_id: {body.group_id}")
    if len(g.trajectory_ids) < 2:
        _err("group must contain at least two trajectories for relative evaluation")
