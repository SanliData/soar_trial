"""
MODULE: evolution_validation_service
PURPOSE: Validate proposals and reject unsafe mutation attempts (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.evolution_governance.mutation_proposal_service import MUTATION_PROPOSALS


class SimulateRequest(BaseModel):
    proposal_id: str = Field(..., min_length=1)
    sandbox_only: bool = True
    request_production_deploy: bool = False

    @field_validator("sandbox_only")
    @classmethod
    def sandbox_only_must_be_true(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("sandbox_only must remain true for foundation API")
        return v


class RollbackCheckRequest(BaseModel):
    proposal_id: str = Field(..., min_length=1)
    mutation_deployed: bool = False
    governance_approval_completed: bool = False
    evaluation_trace_stored: bool = True


def validate_proposal_id(proposal_id: str) -> None:
    key = proposal_id.strip()
    if key not in MUTATION_PROPOSALS:
        raise ValueError("invalid mutation proposal id")


def validate_simulate_request(body: SimulateRequest) -> None:
    validate_proposal_id(body.proposal_id)
    if body.request_production_deploy is True:
        raise ValueError("production deploy is not allowed via evolution sandbox API")


def validate_unsafe_mutation_metadata(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unrestricted_runtime_rewrite") is True:
        raise ValueError("unsafe mutation metadata rejected")
    if meta.get("autonomous_production_mutation") is True:
        raise ValueError("unsafe mutation metadata rejected")
