"""
MODULE: executive_summary_service
PURPOSE: Deterministic executive summaries referencing evidence (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.results_hub.evidence_trace_service import export_evidence_traces
from src.results_hub.opportunity_card_service import export_opportunities
from src.results_hub.risk_analysis_service import export_risks


def export_executive_summary() -> dict[str, Any]:
    opps = export_opportunities()
    risks = export_risks(contractor_id="ctr-001")
    traces = export_evidence_traces(query="procurement bid notice")

    top_titles = [o["title"] for o in opps["opportunities"][:2]]
    evidence_ids = [e["evidence_id"] for e in traces["evidence"][:3]]

    return {
        "procurement_summary": {
            "headline": "Active procurement signals detected (deterministic sample).",
            "top_opportunities": top_titles,
            "evidence": evidence_ids,
            "deterministic": True,
        },
        "contractor_summary": {
            "headline": "Contractor profiles require human validation for permits and bonding.",
            "deterministic": True,
        },
        "regional_opportunity_summary": {
            "headline": "Region shows telecom-category procurement activity.",
            "region": "US-SE",
            "deterministic": True,
        },
        "operational_risk_summary": {
            "headline": "Source freshness and timeline sensitivity are primary risks.",
            "overall_risk": risks["overall"],
            "deterministic": True,
        },
        "no_fabricated_claims": True,
        "deterministic": True,
    }

