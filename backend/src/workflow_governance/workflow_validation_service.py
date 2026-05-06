"""
MODULE: workflow_validation_service
PURPOSE: Request validation models and harness topology checks (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from src.workflow_governance.adaptive_effort_service import EFFORT_LEVELS
from src.workflow_governance.workflow_contract_registry import WORKFLOW_CONTRACTS


class WorkflowSessionCreate(BaseModel):
    workflow_name: str = Field(min_length=1, max_length=128)
    label: Optional[str] = Field(default=None, max_length=256)


class WorkflowCompressRequest(BaseModel):
    context_text: str = Field(default="", max_length=512_000)
    token_estimate: int = Field(default=0, ge=0, le=2_000_000)
    turn_count: int = Field(default=0, ge=0, le=500_000)


class WorkflowValidateRequest(BaseModel):
    workflow_name: str = Field(min_length=1, max_length=128)
    outputs: dict[str, Any] = Field(default_factory=dict)
    constraints_respected: bool = True
    escalation_acknowledged: bool = False


class DelegationValidateRequest(BaseModel):
    workflow_name: str
    delegate_to: str
    depth: int = Field(ge=0, le=10)
    permission: str
    current_subagent_count: int = Field(ge=0, le=100)


def validate_workflow_name(name: str) -> None:
    if name not in WORKFLOW_CONTRACTS:
        raise ValueError(f"invalid workflow_name: {name}")


def validate_effort_level(level: str) -> None:
    if level not in EFFORT_LEVELS:
        raise ValueError(f"invalid effort level: {level}")


def validate_acceptance_structure(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("outputs must be an object")
