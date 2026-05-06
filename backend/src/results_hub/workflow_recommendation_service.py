"""
MODULE: workflow_recommendation_service
PURPOSE: Recommendation routing (no autonomous execution) (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.results_hub.opportunity_card_service import export_opportunities
from src.results_hub.risk_analysis_service import export_risks
from src.results_hub.results_hub_validation_service import reject_hidden_scoring


def export_recommendations() -> dict[str, Any]:
    opps = export_opportunities()
    risks = export_risks(contractor_id="ctr-001")
    top = opps["opportunities"][0] if opps["opportunities"] else None
    overall = risks["overall"]["level"]

    recs = []
    if top:
        recs.append({"action": "review_opportunity", "target_id": top["opportunity_id"], "reason": "high relevance score", "deterministic": True})
    if overall in {"high", "critical"}:
        recs.append({"action": "request_human_review", "target_id": "ctr-001", "reason": "risk level elevated", "deterministic": True})
    recs.append({"action": "request_contractor_validation", "target_id": "ctr-001", "reason": "permits/bonding require verification", "deterministic": True})

    out = {
        "recommendations": recs,
        "recommendations_only": True,
        "autonomous_action_execution": False,
        "hidden_ranking_logic": False,
        "deterministic": True,
    }
    reject_hidden_scoring(out)
    return out

