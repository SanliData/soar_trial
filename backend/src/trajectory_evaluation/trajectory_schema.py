"""
MODULE: trajectory_schema
PURPOSE: Pydantic models for trajectory relative evaluation (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Trajectory(BaseModel):
    trajectory_id: str
    workflow_name: str
    strategy_name: str
    input_summary: str
    output_summary: str
    reasoning_metadata: dict[str, Any] = Field(default_factory=dict)
    evaluation_score: Optional[float] = None
    created_at: datetime = Field(default_factory=_utc_now)
    tags: list[str] = Field(default_factory=list)


class TrajectoryGroup(BaseModel):
    group_id: str
    workflow_name: str
    shared_input_summary: str
    trajectory_ids: list[str] = Field(default_factory=list)
    comparison_notes: str = ""
    created_at: datetime = Field(default_factory=_utc_now)


class RelativeEvaluation(BaseModel):
    evaluation_id: str
    group_id: str
    winning_trajectory_id: str
    ranked_trajectory_ids: list[str] = Field(default_factory=list)
    scoring_reasoning: str
    evaluation_metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utc_now)


class TrajectoryCreateRequest(BaseModel):
    workflow_name: str = Field(..., min_length=1)
    strategy_name: str = Field(..., min_length=1)
    input_summary: str = Field(..., min_length=1)
    output_summary: str = Field(..., min_length=1)
    reasoning_metadata: dict[str, Any] = Field(default_factory=dict)
    evaluation_score: Optional[float] = None
    tags: list[str] = Field(default_factory=list)


class TrajectoryGroupCreateRequest(BaseModel):
    workflow_name: str = Field(..., min_length=1)
    shared_input_summary: str = Field(..., min_length=1)
    trajectory_ids: list[str] = Field(default_factory=list)
    comparison_notes: str = ""


class RelativeEvaluateRequest(BaseModel):
    group_id: str = Field(..., min_length=1)
