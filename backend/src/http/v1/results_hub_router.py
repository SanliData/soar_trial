"""
ROUTER: results_hub_router
PURPOSE: Commercial intelligence results hub API (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.results_hub.contractor_profile_service import export_contractors
from src.results_hub.evidence_trace_service import export_evidence_traces
from src.results_hub.executive_summary_service import export_executive_summary
from src.results_hub.explainability_panel_service import export_explainability_panels
from src.results_hub.opportunity_card_service import export_opportunities
from src.results_hub.relationship_snapshot_service import export_relationships
from src.results_hub.risk_analysis_service import export_risks
from src.results_hub.workflow_recommendation_service import export_recommendations

router = APIRouter(tags=["results-hub"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "commercial_results_hub": True,
        "explainability_mandatory": True,
        "lineage_required": True,
        "autonomous_action_execution": False,
        "deterministic": True,
    }
    merged.update(payload)
    return merged


@router.get("/results/opportunities")
async def get_opportunities() -> Dict[str, Any]:
    return _envelope(export_opportunities())


@router.get("/results/contractors")
async def get_contractors() -> Dict[str, Any]:
    return _envelope(export_contractors())


@router.get("/results/risks")
async def get_risks() -> Dict[str, Any]:
    return _envelope(export_risks(contractor_id="ctr-001"))


@router.get("/results/executive-summary")
async def get_executive_summary() -> Dict[str, Any]:
    return _envelope(export_executive_summary())


@router.get("/results/evidence")
async def get_evidence() -> Dict[str, Any]:
    return _envelope(export_evidence_traces(query="procurement bid notice"))


@router.get("/results/recommendations")
async def get_recommendations() -> Dict[str, Any]:
    return _envelope(export_recommendations())


@router.get("/results/relationships")
async def get_relationships() -> Dict[str, Any]:
    return _envelope(export_relationships())


@router.get("/results/explainability")
async def get_explainability() -> Dict[str, Any]:
    return _envelope(export_explainability_panels())

