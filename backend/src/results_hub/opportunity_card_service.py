"""
MODULE: opportunity_card_service
PURPOSE: Deterministic opportunity card generation with lineage (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.results_hub.evidence_trace_service import export_evidence_traces
from src.results_hub.results_hub_validation_service import ensure_deterministic, reject_hidden_scoring, require_lineage


def _score_relevance(*, authority: float, freshness_days: int, query_hit: bool) -> float:
    base = 0.35
    base += 0.45 * max(0.0, min(1.0, float(authority)))
    base += 0.15 if freshness_days <= 7 else 0.08 if freshness_days <= 30 else 0.02
    base += 0.05 if query_hit else 0.0
    return round(min(1.0, max(0.0, base)), 4)


def export_opportunities(*, region: str = "US-SE", category: str = "telecom") -> dict[str, Any]:
    traces = export_evidence_traces(query="procurement bid notice")
    evidence = traces["evidence"]
    require_lineage(evidence)

    cards = []
    for i, ev in enumerate(evidence[:4], start=1):
        lineage = ev["source_lineage"]
        authority = float(lineage.get("authority_score") or 0.6)
        freshness_days = int(lineage.get("freshness_days") or 14)
        relevance_score = _score_relevance(authority=authority, freshness_days=freshness_days, query_hit=True)
        urgency_level = "high" if freshness_days <= 7 else "elevated" if freshness_days <= 30 else "normal"
        funding_signal = "public_procurement" if "procurement" in (ev["title"] or "").lower() else "unknown"
        estimated_fit = "strong" if relevance_score >= 0.8 else "moderate" if relevance_score >= 0.65 else "weak"

        cards.append(
            {
                "opportunity_id": f"opp-{i:03d}",
                "title": ev["title"],
                "region": region,
                "category": category,
                "relevance_score": relevance_score,
                "funding_signal": funding_signal,
                "urgency_level": urgency_level,
                "estimated_fit": estimated_fit,
                "supporting_evidence": [ev["evidence_id"]],
                "retrieval_sources": [lineage],
                "deterministic": True,
                "hidden_ranking_logic": False,
            }
        )

    out = {"opportunities": cards, "deterministic": True, "lineage_enforced": True}
    reject_hidden_scoring(out)
    ensure_deterministic(out)
    return out

