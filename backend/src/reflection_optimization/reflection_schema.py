"""
MODULE: reflection_schema
PURPOSE: Pydantic models for reflection-driven prompt optimization (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TaskTypeLiteral = Literal[
    "executive_briefing",
    "graph_reasoning",
    "opportunity_ranking",
    "generative_ui_widget",
    "onboarding_planner",
    "market_signal_summary",
]

ApprovalStatusLiteral = Literal["pending", "approved", "rejected", "archived"]


class ReflectionTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(..., min_length=1)
    task_type: TaskTypeLiteral
    workflow_name: str = Field(..., min_length=1)
    input_summary: str = ""
    output_summary: str = ""
    success: bool
    score: float = Field(0.0, ge=0.0, le=1.0)
    failure_modes: List[str] = Field(default_factory=list)
    execution_notes: str = ""
    created_at: datetime


class PromptCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(..., min_length=1)
    workflow_name: str = Field(..., min_length=1)
    current_prompt_summary: str = ""
    proposed_prompt_summary: str = ""
    reflection_reasoning: str = ""
    expected_improvement: str = ""
    human_review_required: bool = True
    approval_status: ApprovalStatusLiteral = "pending"
    created_at: datetime


class OptimizationHistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    history_id: str = Field(..., min_length=1)
    workflow_name: str = Field(..., min_length=1)
    previous_candidate_id: Optional[str] = None
    accepted_candidate_id: Optional[str] = None
    evaluation_notes: str = ""
    approved_by: str = ""
    created_at: datetime


class ReflectionEnvelope(BaseModel):
    """Every reflection API response carries this guardrail flag."""

    autonomous_execution: bool = False


class CreateTraceRequest(BaseModel):
    task_type: TaskTypeLiteral
    workflow_name: str = Field(..., min_length=1)
    input_summary: str = ""
    output_summary: str = ""
    success: bool
    score: float = Field(0.0, ge=0.0, le=1.0)
    failure_modes: List[str] = Field(default_factory=list)
    execution_notes: str = ""


class CreateCandidateFromTraceRequest(BaseModel):
    trace_id: str = Field(..., min_length=1)
    workflow_name: Optional[str] = Field(None, description="Optional override; defaults from trace.")


class ApproveCandidateBody(BaseModel):
    approved_by: str = Field(..., min_length=1)
    evaluation_notes: str = ""


class RejectCandidateBody(BaseModel):
    rejected_by: str = Field(..., min_length=1)
    evaluation_notes: str = ""
