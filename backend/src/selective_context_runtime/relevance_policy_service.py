"""
MODULE: relevance_policy_service
PURPOSE: Deterministic REFRAG-style relevance policy simulation (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def score_relevance_policy(
    *,
    query: str,
    chunk_text: str,
    source_authority: float,
    freshness_days: int,
    workflow_scope: str,
    commercial_relevance: float = 0.6,
    geographic_relevance: float = 0.35,
) -> dict[str, Any]:
    q = (query or "").strip().lower()
    t = (chunk_text or "").strip().lower()
    wf = (workflow_scope or "").strip().lower()

    query_match = 0.35
    if q and any(tok in t for tok in q.split()[:4]):
        query_match = 0.85
    freshness = 1.0 if freshness_days <= 0 else 0.2 if freshness_days >= 365 else round(1.0 - (freshness_days / 365.0) * 0.8, 4)
    workflow_relevance = 0.6
    if "procurement" in wf:
        workflow_relevance = 0.82
    elif "permit" in wf:
        workflow_relevance = 0.74

    weights = {
        "query_match": 0.32,
        "source_authority": 0.22,
        "freshness": 0.18,
        "workflow_relevance": 0.14,
        "commercial_relevance": 0.08,
        "geographic_relevance": 0.06,
    }
    total = (
        weights["query_match"] * query_match
        + weights["source_authority"] * _clamp01(source_authority)
        + weights["freshness"] * _clamp01(freshness)
        + weights["workflow_relevance"] * workflow_relevance
        + weights["commercial_relevance"] * _clamp01(commercial_relevance)
        + weights["geographic_relevance"] * _clamp01(geographic_relevance)
    )
    return {
        "score": round(_clamp01(total), 4),
        "factors": {
            "query_match": round(query_match, 4),
            "source_authority": round(_clamp01(source_authority), 4),
            "freshness": round(_clamp01(freshness), 4),
            "workflow_relevance": round(workflow_relevance, 4),
            "commercial_relevance": round(_clamp01(commercial_relevance), 4),
            "geographic_relevance": round(_clamp01(geographic_relevance), 4),
        },
        "weights": dict(weights),
        "deterministic": True,
        "rl_training_enabled": False,
    }

