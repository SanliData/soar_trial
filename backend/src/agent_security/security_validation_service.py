"""
MODULE: security_validation_service
PURPOSE: Validate trust inputs and boundary requests (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from src.agent_security.tool_capability_registry import TRUST_LEVELS


class SanitizePromptRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SanitizeRetrievalRequest(BaseModel):
    content: str = Field(..., min_length=1)
    content_type: str = Field(default="html")


class RiskScoreRequest(BaseModel):
    prompt_text: str = Field(..., min_length=1)
    retrieval_sample: str = ""
    requested_tools: list[str] = Field(default_factory=list)


class BoundaryCheckRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    action: str = Field(..., min_length=1)
    domain: Optional[str] = None


class DelegationCheckRequest(BaseModel):
    source_tool: str = Field(..., min_length=1)
    target_tool: str = Field(..., min_length=1)


def validate_trust_level(level: str) -> None:
    if level not in TRUST_LEVELS:
        raise ValueError(f"invalid trust_level: {level}")
