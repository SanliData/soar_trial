"""
ROUTER: ensemble_governance_router
PURPOSE: HTTP facade for ensemble governance (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.ensemble_governance.consensus_scoring_service import export_consensus_scoring_manifest
from src.ensemble_governance.evaluation_randomization_service import export_evaluation_randomization_manifest
from src.ensemble_governance.multi_evaluator_service import export_multi_evaluator_manifest
from src.ensemble_governance.variance_detection_service import export_variance_detection_manifest

router = APIRouter(tags=["ensemble-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "ensemble_governance_foundation": True,
        "hidden_ensemble_weighting": False,
        "autonomous_evaluator_swarm": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/ensemble/evaluators")
async def get_ensemble_evaluators() -> Dict[str, Any]:
    return _envelope({"evaluators": export_multi_evaluator_manifest()})


@router.get("/system/ensemble/consensus")
async def get_ensemble_consensus() -> Dict[str, Any]:
    return _envelope({"consensus": export_consensus_scoring_manifest()})


@router.get("/system/ensemble/variance")
async def get_ensemble_variance() -> Dict[str, Any]:
    return _envelope({"variance": export_variance_detection_manifest()})


@router.get("/system/ensemble/randomization")
async def get_ensemble_randomization() -> Dict[str, Any]:
    return _envelope({"randomization": export_evaluation_randomization_manifest()})
