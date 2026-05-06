"""
MODULE: evaluation_trace_service
PURPOSE: Append-only relative evaluation records — auditable traces (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.trajectory_evaluation.comparison_reasoning_service import build_evaluation_narrative
from src.trajectory_evaluation.relative_scoring_service import rank_trajectories
from src.trajectory_evaluation.trajectory_registry import TrajectoryStore, new_id
from src.trajectory_evaluation.trajectory_schema import RelativeEvaluation, Trajectory


def execute_relative_evaluation(store: TrajectoryStore, group_id: str) -> RelativeEvaluation:
    """
    Deterministic relative ranking for a group; persists evaluation without muting prior scores.
    """
    group = store.get_group(group_id)
    if group is None:
        raise ValueError(f"unknown group_id: {group_id}")
    trajs: list[Trajectory] = []
    for tid in group.trajectory_ids:
        t = store.get_trajectory(tid)
        if t is None:
            raise ValueError(f"missing trajectory in store: {tid}")
        trajs.append(t)
    if len(trajs) < 2:
        raise ValueError("group must contain at least two trajectories for relative evaluation")

    ranked_ids, score_meta = rank_trajectories(trajs)
    narrative = build_evaluation_narrative(ranked_ids, score_meta)

    ev = RelativeEvaluation(
        evaluation_id=new_id("eval"),
        group_id=group_id,
        winning_trajectory_id=ranked_ids[0],
        ranked_trajectory_ids=ranked_ids,
        scoring_reasoning=narrative,
        evaluation_metadata={
            "per_trajectory": score_meta,
            "policy": "deterministic_weighted_linear_v1",
            "comparison_style": "template_based_visible_factors",
        },
    )
    store.put_evaluation(ev)
    return ev


def list_evaluation_traces(store: TrajectoryStore) -> list[RelativeEvaluation]:
    return sorted(store.list_evaluations(), key=lambda e: e.created_at)
