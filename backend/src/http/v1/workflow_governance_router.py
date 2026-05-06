"""
ROUTER: workflow_governance_router
PURPOSE: HTTP facade for workflow governance (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.workflow_governance.adaptive_effort_service import export_effort_manifest
from src.workflow_governance.context_decay_service import workflow_compress_bundle
from src.workflow_governance.workflow_acceptance_service import evaluate_acceptance
from src.workflow_governance.workflow_contract_registry import export_contracts_manifest
from src.workflow_governance.workflow_session_service import (
    create_session,
    get_governance_runtime_summary,
)
from src.workflow_governance.workflow_validation_service import (
    WorkflowCompressRequest,
    WorkflowSessionCreate,
    WorkflowValidateRequest,
    validate_acceptance_structure,
)

router = APIRouter(prefix="/system/workflows", tags=["workflow-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "workflow_governance_foundation": True,
        "unrestricted_autonomous_execution": False,
        "recursive_workflow_swarm": False,
    }
    merged.update(payload)
    return merged


@router.get("/contracts")
async def get_contracts() -> Dict[str, Any]:
    return _envelope(export_contracts_manifest())


@router.get("/effort-levels")
async def get_effort_levels() -> Dict[str, Any]:
    return _envelope(export_effort_manifest())


@router.post("/session")
async def post_session(body: WorkflowSessionCreate) -> Dict[str, Any]:
    try:
        return _envelope(create_session(body.workflow_name, body.label))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/compress")
async def post_compress(body: WorkflowCompressRequest) -> Dict[str, Any]:
    bundle = workflow_compress_bundle(body.context_text, body.token_estimate, body.turn_count)
    return _envelope({"workflow_compression": bundle})


@router.post("/validate")
async def post_validate(body: WorkflowValidateRequest) -> Dict[str, Any]:
    try:
        validate_acceptance_structure(body.outputs)
        result = evaluate_acceptance(
            body.workflow_name,
            body.outputs,
            body.constraints_respected,
            body.escalation_acknowledged,
        )
        return _envelope({"acceptance": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/runtime-summary")
async def get_runtime_summary() -> Dict[str, Any]:
    return _envelope({"summary": get_governance_runtime_summary()})
