"""
MODULE: trajectory_group_service
PURPOSE: Group trajectories for same-workflow relative comparison (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.trajectory_evaluation.trajectory_registry import TrajectoryStore, new_id
from src.trajectory_evaluation.trajectory_schema import TrajectoryGroup, TrajectoryGroupCreateRequest
from src.trajectory_evaluation.trajectory_validation_service import validate_group_create


def create_group(store: TrajectoryStore, body: TrajectoryGroupCreateRequest) -> TrajectoryGroup:
    validate_group_create(body, store)
    gid = new_id("grp")
    group = TrajectoryGroup(
        group_id=gid,
        workflow_name=body.workflow_name,
        shared_input_summary=body.shared_input_summary,
        trajectory_ids=list(body.trajectory_ids),
        comparison_notes=body.comparison_notes or "",
    )
    store.put_group(group)
    return group


def add_trajectory(store: TrajectoryStore, group_id: str, trajectory_id: str) -> TrajectoryGroup:
    g = store.get_group(group_id)
    if g is None:
        raise ValueError(f"unknown group_id: {group_id}")
    t = store.get_trajectory(trajectory_id)
    if t is None:
        raise ValueError(f"unknown trajectory_id: {trajectory_id}")
    if t.workflow_name != g.workflow_name:
        raise ValueError("trajectory workflow_name must match group workflow_name")
    ids = list(g.trajectory_ids)
    if trajectory_id not in ids:
        ids.append(trajectory_id)
    updated = g.model_copy(update={"trajectory_ids": ids})
    store.put_group(updated)
    return updated


def summarize_group(store: TrajectoryStore, group_id: str) -> dict[str, Any]:
    g = store.get_group(group_id)
    if g is None:
        raise ValueError(f"unknown group_id: {group_id}")
    return {
        "group_id": g.group_id,
        "workflow_name": g.workflow_name,
        "trajectory_count": len(g.trajectory_ids),
        "trajectory_ids": list(g.trajectory_ids),
        "shared_input_summary": g.shared_input_summary,
        "comparison_notes": g.comparison_notes,
    }
