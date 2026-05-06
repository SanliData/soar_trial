"""
MODULE: explainability_panel_service
PURPOSE: Explainability panels: why, evidence, scoring, freshness, confidence (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.results_hub.evidence_trace_service import export_evidence_traces
from src.results_hub.opportunity_card_service import export_opportunities
from src.results_hub.results_hub_validation_service import ensure_deterministic, reject_hidden_scoring


def _confidence_indicator(*, evidence_count: int, avg_authority: float) -> str:
    if evidence_count >= 4 and avg_authority >= 0.8:
        return "high"
    if evidence_count >= 2 and avg_authority >= 0.65:
        return "moderate"
    return "low"


def export_explainability_panels() -> dict[str, Any]:
    opps = export_opportunities()
    traces = export_evidence_traces(query="procurement bid notice")
    evidence = traces["evidence"]
    auth = [float(e["source_lineage"].get("authority_score") or 0.6) for e in evidence] if evidence else [0.6]
    avg_auth = round(sum(auth) / len(auth), 4)

    panels = []
    for o in opps["opportunities"][:3]:
        panels.append(
            {
                "opportunity_id": o["opportunity_id"],
                "why_this_appeared": ["matched deterministic procurement query", "connector registry enabled sources", "lineage validated"],
                "retrieval_evidence": o["supporting_evidence"],
                "scoring_explanation": {"relevance_score": o["relevance_score"], "inputs": ["authority_score", "freshness_days", "query_hit"], "hidden_ranking_logic": False},
                "freshness_explanation": "derived from connector freshness metadata; no live sync",
                "confidence_indicators": {"confidence": _confidence_indicator(evidence_count=len(evidence), avg_authority=avg_auth), "avg_authority": avg_auth},
                "deterministic": True,
            }
        )

    out = {"explainability": panels, "deterministic": True, "hidden_ranking_logic": False}
    reject_hidden_scoring(out)
    ensure_deterministic(out)
    return out

