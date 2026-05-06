"""
MODULE: feedback_contracts
PURPOSE: Deterministic structured failure/signal codes — no LLM reasoning (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Dict, FrozenSet

# Canonical catalog — orchestrators select from this set (deterministic strings).
STRUCTURED_FAILURE_CODES: FrozenSet[str] = frozenset(
    {
        "missing_market_context",
        "weak_geographic_targeting",
        "low_confidence_graph_edge",
        "repeated_opportunity_cluster",
        "overly_generic_executive_summary",
        "poor_signal_prioritization",
    }
)

# Deterministic recommendation strings keyed by failure code (template library).
DETERMINISTIC_RECOMMENDATIONS: Dict[str, str] = {
    "missing_market_context": (
        "Add stronger market-context guidance: require explicit industry, segment, and timing cues "
        "before synthesis steps."
    ),
    "weak_geographic_targeting": (
        "Add stronger geographic constraint guidance: anchor regions, metros, or radius language "
        "in prompts and downstream filters."
    ),
    "low_confidence_graph_edge": (
        "Add graph-edge validation guidance: surface confidence scores and exclude ambiguous "
        "relationships from downstream reasoning."
    ),
    "repeated_opportunity_cluster": (
        "Add deduplication guidance: collapse redundant clusters and steer prompts toward novel angles."
    ),
    "overly_generic_executive_summary": (
        "Add specificity scaffolding: force metric-backed bullets and named signals in summaries."
    ),
    "poor_signal_prioritization": (
        "Add prioritization rubric: rank signals by severity, recency, and commercial relevance."
    ),
}


def recommendation_for_code(code: str) -> str:
    """Return deterministic recommendation text or a generic fallback."""
    if code in DETERMINISTIC_RECOMMENDATIONS:
        return DETERMINISTIC_RECOMMENDATIONS[code]
    return (
        f"Review structured failure code '{code}' and extend feedback_contracts.py "
        "with an explicit deterministic recommendation template."
    )
