"""
MODULE: runtime_schema
PURPOSE: Pydantic schemas for inference-aware AI runtime foundation (H-021)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TaskTypeLiteral = Literal[
    "executive_briefing",
    "graph_reasoning",
    "generative_ui_widget",
    "opportunity_ranking",
    "market_signal_summary",
    "analytics_summary",
]

QualityTierLiteral = Literal["economy", "standard", "premium"]

ProfileStatusLiteral = Literal["ready", "adjusted", "invalid_budget"]


class AIRuntimeTask(BaseModel):
    """Declarative task envelope for runtime planning (no LLM execution)."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(..., min_length=1)
    task_type: TaskTypeLiteral
    requested_quality_tier: QualityTierLiteral
    max_input_tokens: int = Field(..., ge=1, le=1_000_000)
    max_output_tokens: int = Field(..., ge=1, le=500_000)
    latency_target_ms: int = Field(..., ge=1)
    allow_compaction: bool = True
    preferred_model: Optional[str] = Field(None, description="Optional override for routing experiments.")


class AIRuntimeProfile(BaseModel):
    """Telemetry-oriented runtime profile after deterministic budgeting (no inference)."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    task_type: TaskTypeLiteral
    selected_model: str
    model_family: str
    quality_tier: QualityTierLiteral
    estimated_input_tokens: int = Field(..., ge=0)
    estimated_output_tokens: int = Field(..., ge=0)
    estimated_total_tokens: int = Field(..., ge=0)
    prompt_compaction_applied: bool
    latency_ms: int = Field(..., ge=0)
    time_to_first_token_ms: Optional[int] = Field(
        None,
        description="Synthetic planning estimate when live TTFT is unavailable.",
    )
    status: ProfileStatusLiteral
    warnings: List[str] = Field(default_factory=list)


class TokenBudgetResult(BaseModel):
    """Outcome of deterministic token budget enforcement."""

    model_config = ConfigDict(extra="forbid")

    text: str
    truncated: bool
    warning: Optional[str] = None


class CompactionResult(BaseModel):
    """Outcome of deterministic prompt compaction."""

    model_config = ConfigDict(extra="forbid")

    compacted_text: str
    original_estimated_tokens: int
    compacted_estimated_tokens: int
    compaction_applied: bool


class AIRuntimeProfileResponse(BaseModel):
    """HTTP envelope: callers must never infer an LLM executed."""

    llm_invoked: bool = False
    profile: AIRuntimeProfile


class AIRuntimeProfilesListResponse(BaseModel):
    llm_invoked: bool = False
    profiles: List[AIRuntimeProfile]


class ProfileBuildRequest(BaseModel):
    task: AIRuntimeTask
    input_context: str = Field("", description="Raw contextual payload used only for sizing.")
