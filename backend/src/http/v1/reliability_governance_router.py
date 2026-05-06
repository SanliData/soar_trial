"""
ROUTER: reliability_governance_router
PURPOSE: HTTP facade for reliability governance (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from src.reliability_governance.context_stability_service import export_context_stability
from src.reliability_governance.drift_monitoring_service import export_drift_report
from src.reliability_governance.embedding_health_service import export_embedding_health
from src.reliability_governance.evaluation_governance_service import export_evaluation_governance
from src.reliability_governance.retrieval_quality_service import export_retrieval_quality
from src.reliability_governance.runtime_observability_service import export_observability_traces
from src.reliability_governance.workflow_reliability_service import export_workflow_reliability
from src.reliability_governance.reliability_validation_service import validate_ratio

router = APIRouter(prefix="/system/reliability", tags=["reliability-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "reliability_governance_foundation": True,
        "distributed_observability_mesh": False,
        "uncontrolled_monitoring_sprawl": False,
    }
    merged.update(payload)
    return merged


def _vr(name: str, v: float) -> float:
    try:
        return validate_ratio(name, v)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/drift")
async def get_drift(
    retrieval_drift_signal: float = Query(0.0),
    graph_drift_signal: float = Query(0.0),
    prompt_drift_signal: float = Query(0.0),
    workflow_drift_signal: float = Query(0.0),
    embedding_drift_signal: float = Query(0.0),
    context_drift_signal: float = Query(0.0),
    suite_version_age_days: float = Query(0.0),
    missing_coverage_ratio: float = Query(0.0),
    comparison_weak_ratio: float = Query(0.0),
    inconsistent_run_ratio: float = Query(0.0),
) -> Dict[str, Any]:
    metrics = {
        "retrieval_drift_signal": _vr("retrieval_drift_signal", retrieval_drift_signal),
        "graph_drift_signal": _vr("graph_drift_signal", graph_drift_signal),
        "prompt_drift_signal": _vr("prompt_drift_signal", prompt_drift_signal),
        "workflow_drift_signal": _vr("workflow_drift_signal", workflow_drift_signal),
        "embedding_drift_signal": _vr("embedding_drift_signal", embedding_drift_signal),
        "context_drift_signal": _vr("context_drift_signal", context_drift_signal),
    }
    drift = export_drift_report(metrics)
    evaluation = export_evaluation_governance(
        suite_version_age_days=float(suite_version_age_days),
        missing_coverage_ratio=_vr("missing_coverage_ratio", missing_coverage_ratio),
        comparison_weak_ratio=_vr("comparison_weak_ratio", comparison_weak_ratio),
        inconsistent_run_ratio=_vr("inconsistent_run_ratio", inconsistent_run_ratio),
    )
    return _envelope({"drift": drift, "evaluation_governance": evaluation})


@router.get("/retrieval")
async def get_retrieval(
    duplicate_ratio: float = Query(0.0),
    stale_context_ratio: float = Query(0.0),
    low_authority_ratio: float = Query(0.0),
    weak_graph_link_ratio: float = Query(0.0),
    relevance_decay: float = Query(0.0),
) -> Dict[str, Any]:
    payload = export_retrieval_quality(
        duplicate_ratio=_vr("duplicate_ratio", duplicate_ratio),
        stale_context_ratio=_vr("stale_context_ratio", stale_context_ratio),
        low_authority_ratio=_vr("low_authority_ratio", low_authority_ratio),
        weak_graph_link_ratio=_vr("weak_graph_link_ratio", weak_graph_link_ratio),
        relevance_decay=_vr("relevance_decay", relevance_decay),
    )
    return _envelope({"retrieval": payload})


@router.get("/embeddings")
async def get_embeddings(
    stale_ratio: float = Query(0.0),
    missing_ratio: float = Query(0.0),
    low_confidence_ratio: float = Query(0.0),
    max_age_hours: float = Query(0.0),
    invalid_source_ratio: float = Query(0.0),
) -> Dict[str, Any]:
    if max_age_hours < 0:
        raise HTTPException(status_code=422, detail="max_age_hours must be non-negative")
    payload = export_embedding_health(
        stale_ratio=_vr("stale_ratio", stale_ratio),
        missing_ratio=_vr("missing_ratio", missing_ratio),
        low_confidence_ratio=_vr("low_confidence_ratio", low_confidence_ratio),
        max_age_hours=float(max_age_hours),
        invalid_source_ratio=_vr("invalid_source_ratio", invalid_source_ratio),
    )
    return _envelope({"embeddings": payload})


@router.get("/workflows")
async def get_workflows(
    token_estimate: int = Query(0),
    retry_count: int = Query(0),
    delegation_flap_count: int = Query(0),
    acceptance_failure_ratio: float = Query(0.0),
    context_rot_score: float = Query(0.0),
) -> Dict[str, Any]:
    for name, v in (
        ("acceptance_failure_ratio", acceptance_failure_ratio),
        ("context_rot_score", context_rot_score),
    ):
        _vr(name, float(v))
    if token_estimate < 0 or retry_count < 0 or delegation_flap_count < 0:
        raise HTTPException(status_code=422, detail="counts must be non-negative")
    payload = export_workflow_reliability(
        token_estimate=int(token_estimate),
        retry_count=int(retry_count),
        delegation_flap_count=int(delegation_flap_count),
        acceptance_failure_ratio=float(acceptance_failure_ratio),
        context_rot_score=float(context_rot_score),
    )
    return _envelope({"workflows": payload})


@router.get("/context")
async def get_context(
    rot_score: float = Query(0.0),
    context_chars: int = Query(0),
    summarization_jump_ratio: float = Query(0.0),
    metadata_inconsistency_ratio: float = Query(0.0),
) -> Dict[str, Any]:
    payload = export_context_stability(
        rot_score=_vr("rot_score", rot_score),
        context_chars=max(0, int(context_chars)),
        summarization_jump_ratio=_vr("summarization_jump_ratio", summarization_jump_ratio),
        metadata_inconsistency_ratio=_vr("metadata_inconsistency_ratio", metadata_inconsistency_ratio),
    )
    return _envelope({"context": payload})


@router.get("/traces")
async def get_traces(
    include_examples: bool = Query(True),
) -> Dict[str, Any]:
    payload = export_observability_traces(include_examples=include_examples)
    return _envelope({"observability": payload})
