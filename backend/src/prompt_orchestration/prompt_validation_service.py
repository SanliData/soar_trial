"""
MODULE: prompt_validation_service
PURPOSE: Validate strategies, personas, contracts for orchestration requests (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from src.prompt_orchestration.arq_template_service import ALLOWED_ARQ_TEMPLATE_IDS
from src.prompt_orchestration.json_contract_service import list_contract_ids
from src.prompt_orchestration.prompt_strategy_registry import ALLOWED_STRATEGIES
from src.prompt_orchestration.role_prompt_service import ALLOWED_PERSONAS


class EvaluatePromptRequest(BaseModel):
    task_type: str = Field(..., min_length=1)
    strategy_override: Optional[str] = None
    persona: Optional[str] = None
    contract_id: Optional[str] = None
    arq_template_id: Optional[str] = None
    include_negative_constraints: bool = False


def validate_strategy(strategy_id: Optional[str]) -> None:
    if strategy_id is None:
        return
    if strategy_id not in ALLOWED_STRATEGIES:
        raise ValueError(f"invalid strategy: {strategy_id}")


def validate_persona(persona_id: Optional[str]) -> None:
    if persona_id is None:
        return
    if persona_id not in ALLOWED_PERSONAS:
        raise ValueError(f"invalid persona: {persona_id}")


def validate_contract(contract_id: Optional[str]) -> None:
    if contract_id is None:
        return
    if contract_id not in list_contract_ids():
        raise ValueError(f"invalid contract_id: {contract_id}")


def validate_arq_template(template_id: Optional[str]) -> None:
    if template_id is None:
        return
    if template_id not in ALLOWED_ARQ_TEMPLATE_IDS:
        raise ValueError(f"invalid arq_template_id: {template_id}")


def validate_evaluate_request(body: EvaluatePromptRequest) -> None:
    validate_strategy(body.strategy_override)
    validate_persona(body.persona)
    validate_contract(body.contract_id)
    validate_arq_template(body.arq_template_id)
