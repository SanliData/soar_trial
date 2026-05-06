"""
MODULE: trajectory_registry
PURPOSE: In-memory append-only trajectory store — immutable history (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import uuid
from threading import Lock
from typing import Optional

from src.trajectory_evaluation.trajectory_schema import (
    RelativeEvaluation,
    Trajectory,
    TrajectoryCreateRequest,
    TrajectoryGroup,
)


class TrajectoryStore:
    """
    Deterministic single-process store. No autonomous deletion.
    Trajectories and evaluations are append-only records for audit.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._trajectories: dict[str, Trajectory] = {}
        self._groups: dict[str, TrajectoryGroup] = {}
        self._evaluations: dict[str, RelativeEvaluation] = {}

    def put_trajectory(self, trajectory: Trajectory) -> None:
        with self._lock:
            self._trajectories[trajectory.trajectory_id] = trajectory

    def get_trajectory(self, trajectory_id: str) -> Optional[Trajectory]:
        with self._lock:
            return self._trajectories.get(trajectory_id)

    def list_trajectories(self) -> list[Trajectory]:
        with self._lock:
            return list(self._trajectories.values())

    def put_group(self, group: TrajectoryGroup) -> None:
        with self._lock:
            self._groups[group.group_id] = group

    def get_group(self, group_id: str) -> Optional[TrajectoryGroup]:
        with self._lock:
            return self._groups.get(group_id)

    def list_groups(self) -> list[TrajectoryGroup]:
        with self._lock:
            return list(self._groups.values())

    def put_evaluation(self, evaluation: RelativeEvaluation) -> None:
        with self._lock:
            self._evaluations[evaluation.evaluation_id] = evaluation

    def get_evaluation(self, evaluation_id: str) -> Optional[RelativeEvaluation]:
        with self._lock:
            return self._evaluations.get(evaluation_id)

    def list_evaluations(self) -> list[RelativeEvaluation]:
        with self._lock:
            return list(self._evaluations.values())

    def clear(self) -> None:
        """Test helper only — not exposed via API."""
        with self._lock:
            self._trajectories.clear()
            self._groups.clear()
            self._evaluations.clear()


_store = TrajectoryStore()


def get_trajectory_store() -> TrajectoryStore:
    return _store


def reset_trajectory_store_for_tests() -> None:
    _store.clear()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def create_trajectory(store: TrajectoryStore, body: TrajectoryCreateRequest) -> Trajectory:
    from src.trajectory_evaluation.trajectory_validation_service import validate_create_trajectory

    validate_create_trajectory(body)
    tid = new_id("tr")
    traj = Trajectory(
        trajectory_id=tid,
        workflow_name=body.workflow_name,
        strategy_name=body.strategy_name,
        input_summary=body.input_summary,
        output_summary=body.output_summary,
        reasoning_metadata=dict(body.reasoning_metadata),
        evaluation_score=body.evaluation_score,
        tags=list(body.tags),
    )
    store.put_trajectory(traj)
    return traj
