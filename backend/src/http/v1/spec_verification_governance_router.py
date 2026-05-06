"""
ROUTER: spec_verification_governance_router
PURPOSE: HTTP facade for spec verification governance (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.spec_verification_governance.acceptance_criteria_service import validate_acceptance
from src.spec_verification_governance.architecture_contract_service import export_architecture_contracts
from src.spec_verification_governance.review_governance_service import export_review_status
from src.spec_verification_governance.spec_validation_service import (
    SpecValidateRequest,
    TraceToEvalRequest,
    validate_outputs_structure,
    validate_spec_id,
)
from src.spec_verification_governance.specification_registry import export_specifications_manifest
from src.spec_verification_governance.trace_to_eval_service import map_trace_to_eval
from src.spec_verification_governance.verification_trace_service import export_verification_traces

router = APIRouter(tags=["spec-verification-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "spec_verification_foundation": True,
        "autonomous_architecture_mutation": False,
        "unrestricted_autonomous_engineering": False,
        "recursive_self_modifying_governance": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/specs")
async def list_specifications() -> Dict[str, Any]:
    return _envelope({"specifications": export_specifications_manifest()})


@router.get("/system/specs/contracts")
async def list_architecture_contracts() -> Dict[str, Any]:
    return _envelope({"architecture": export_architecture_contracts()})


@router.post("/system/specs/validate")
async def post_validate(body: SpecValidateRequest) -> Dict[str, Any]:
    try:
        validate_spec_id(body.spec_id)
        validate_outputs_structure(body.outputs)
        result = validate_acceptance(
            body.spec_id,
            body.outputs,
            constraints_respected=body.constraints_respected,
            escalation_acknowledged=body.escalation_acknowledged,
            architecture_contracts_ok=body.architecture_contracts_ok,
        )
        return _envelope({"acceptance": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/system/specs/traces")
async def list_traces() -> Dict[str, Any]:
    return _envelope({"verification_traces": export_verification_traces()})


@router.post("/system/specs/trace-to-eval")
async def post_trace_to_eval(body: TraceToEvalRequest) -> Dict[str, Any]:
    try:
        mapped = map_trace_to_eval(body.trace_category, body.trace_code)
        return _envelope({"trace_to_eval": mapped})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/system/specs/review-status")
async def get_review_status_route() -> Dict[str, Any]:
    return _envelope({"review": export_review_status()})
