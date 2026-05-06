"""
MODULE: risk_analysis_service
PURPOSE: Deterministic risk analysis with explainable rules (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.results_hub.connector_freshness_risk import assess_source_freshness_risk


def _risk_level(score: int) -> str:
    if score <= 1:
        return "low"
    if score <= 3:
        return "moderate"
    if score <= 6:
        return "high"
    return "critical"


def export_risks(*, contractor_id: str = "ctr-001") -> dict[str, Any]:
    freshness = assess_source_freshness_risk()
    freshness_score = int(freshness["risk_score"])

    bonding = {"risk_score": 1, "explain": "default bonding metadata-only; no external check", "level": "moderate"}
    permit = {"risk_score": 1, "explain": "permit timeline unknown; require municipality validation", "level": "moderate"}
    compliance = {"risk_score": 0, "explain": "no compliance alerts in deterministic sample", "level": "low"}
    timeline = {"risk_score": 2, "explain": "schedule sensitivity inferred from urgency metadata", "level": "high"}
    dependency = {"risk_score": 1, "explain": "subcontractor dependency present for some scopes", "level": "moderate"}
    source_freshness = {"risk_score": freshness_score, "explain": freshness["explain"], "level": _risk_level(freshness_score)}

    total = sum(int(x["risk_score"]) for x in [bonding, permit, compliance, timeline, dependency, source_freshness])
    return {
        "contractor_id": contractor_id,
        "risks": {
            "bonding_risk": bonding,
            "permit_risk": permit,
            "compliance_risk": compliance,
            "timeline_risk": timeline,
            "contractor_dependency_risk": dependency,
            "source_freshness_risk": source_freshness,
        },
        "overall": {"risk_score": total, "level": _risk_level(total), "deterministic": True},
        "deterministic": True,
        "no_hidden_scoring": True,
    }

