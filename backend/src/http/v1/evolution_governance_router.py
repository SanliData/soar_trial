"""
ROUTER: evolution_governance_router
PURPOSE: HTTP facade for evolution governance (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.evolution_governance.evolution_trace_service import export_evolution_traces
from src.evolution_governance.evolution_validation_service import (
    RollbackCheckRequest,
    SimulateRequest,
    validate_simulate_request,
)
from src.evolution_governance.mutation_proposal_service import export_mutation_proposals_manifest
from src.evolution_governance.policy_evolution_service import export_policy_evolution_manifest
from src.evolution_governance.rollback_governance_service import assess_rollback_readiness
from src.evolution_governance.sandbox_evaluation_service import run_simulation_bundle

router = APIRouter(tags=["evolution-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "evolution_governance_foundation": True,
        "unrestricted_runtime_self_modification": False,
        "autonomous_production_mutation": False,
        "recursive_evolution_loops": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/evolution/proposals")
async def list_proposals() -> Dict[str, Any]:
    return _envelope({"mutation_proposals": export_mutation_proposals_manifest()})


@router.post("/system/evolution/simulate")
async def post_simulate(body: SimulateRequest) -> Dict[str, Any]:
    try:
        validate_simulate_request(body)
        bundle = run_simulation_bundle(body.proposal_id.strip())
        return _envelope({"simulation": bundle})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/system/evolution/traces")
async def list_evolution_traces() -> Dict[str, Any]:
    return _envelope({"evolution_traces": export_evolution_traces()})


@router.post("/system/evolution/rollback-check")
async def post_rollback_check(body: RollbackCheckRequest) -> Dict[str, Any]:
    try:
        result = assess_rollback_readiness(
            body.proposal_id.strip(),
            mutation_deployed=body.mutation_deployed,
            governance_approval_completed=body.governance_approval_completed,
            evaluation_trace_stored=body.evaluation_trace_stored,
        )
        return _envelope({"rollback": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/system/evolution/policies")
async def list_policies() -> Dict[str, Any]:
    return _envelope({"policy_evolution": export_policy_evolution_manifest()})
