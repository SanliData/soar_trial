"""
MODULE: spec_validation_service
PURPOSE: Request models and structural validators (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from src.spec_verification_governance.specification_registry import SPECIFICATIONS


class SpecValidateRequest(BaseModel):
    spec_id: str = Field(min_length=1, max_length=128)
    outputs: dict[str, Any] = Field(default_factory=dict)
    constraints_respected: bool = True
    escalation_acknowledged: bool = False
    architecture_contracts_ok: bool = True


class TraceToEvalRequest(BaseModel):
    trace_category: str = Field(min_length=1, max_length=128)
    trace_code: str = Field(default="generic", max_length=128)


def validate_spec_id(spec_id: str) -> None:
    if spec_id not in SPECIFICATIONS:
        raise ValueError(f"invalid specification id: {spec_id}")


def validate_outputs_structure(outputs: dict[str, Any]) -> None:
    if not isinstance(outputs, dict):
        raise ValueError("outputs must be an object")
