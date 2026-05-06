"""
MODULE: capability_schema
PURPOSE: Pydantic schema for semantic backend capability declarations (H-020)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field

from src.semantic_capabilities.capability_types import RiskLevelLiteral


class CapabilityDefinition(BaseModel):
    """Machine-readable semantic contract for one HTTP capability surface."""

    model_config = ConfigDict(extra="forbid")

    capability_id: str = Field(..., min_length=1, description="Stable dotted identifier.")
    name: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

    endpoint: str = Field(..., description="Path template as mounted in FinderOS.")
    http_method: str = Field(..., pattern=r"^[A-Z]+$")

    auth_required: bool
    idempotent: bool
    rate_limit: str = Field(
        ...,
        description="Human/machine summary of enforced limits (never raw env/secrets).",
    )
    risk_level: RiskLevelLiteral

    sensitive_fields: List[str] = Field(
        default_factory=list,
        description="Field names touched in request/response that may carry PII or firmographics.",
    )
    destructive_action: bool = Field(
        ..., description="True if writes may delete/disable customer-owned material."
    )
    orchestration_safe: bool = Field(
        ...,
        description="Agents may enqueue this capability as a bounded read/analysis step.",
    )
    human_approval_required: bool = Field(
        ...,
        description="Planner must surface explicit approval before invoking (exports, campaigns, launches).",
    )

    allowed_roles: List[str] = Field(default_factory=list)
    input_schema_summary: str = Field(...)
    output_schema_summary: str = Field(...)
    tags: List[str] = Field(default_factory=list)
