"""
ROUTER: prompt_orchestration_router
PURPOSE: HTTP facade for prompt orchestration registry & evaluation (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.prompt_orchestration.arq_template_service import export_arq_manifest
from src.prompt_orchestration.prompt_evaluation_service import evaluate_prompt_configuration
from src.prompt_orchestration.prompt_strategy_registry import export_strategies_manifest
from src.prompt_orchestration.prompt_validation_service import EvaluatePromptRequest
from src.prompt_orchestration.role_prompt_service import export_personas_manifest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/prompts", tags=["prompt-orchestration"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "deterministic_prompt_orchestration": True,
        "autonomous_prompt_evolution": False,
        "chain_of_thought_exposure": "none",
    }
    out.update(payload)
    return out


@router.get("/strategies")
async def get_strategies() -> Dict[str, Any]:
    return _envelope(export_strategies_manifest())


@router.get("/personas")
async def get_personas() -> Dict[str, Any]:
    return _envelope(export_personas_manifest())


@router.get("/arq-templates")
async def get_arq_templates() -> Dict[str, Any]:
    return _envelope(export_arq_manifest())


@router.post("/evaluate")
async def post_evaluate(body: EvaluatePromptRequest) -> Dict[str, Any]:
    try:
        return _envelope({"evaluation": evaluate_prompt_configuration(body)})
    except ValueError as exc:
        logger.info("prompt evaluation rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
