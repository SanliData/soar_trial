"""
MODULE: retrieval_relevance_service
PURPOSE: Deterministic retrieval relevance scoring (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.knowledge_ingestion.source_registry import registry_trust_for, require_approved_source


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _freshness_score(freshness_days: int) -> float:
    if freshness_days <= 0:
        return 1.0
    if freshness_days >= 365:
        return 0.2
    return round(1.0 - (freshness_days / 365.0) * 0.8, 4)


def score_retrieval_relevance(
    *,
    source_type: str,
    freshness_days: int,
    workflow_scope: str,
    geographic_scope: str | None = None,
    commercial_relevance: float | None = None,
) -> dict[str, Any]:
    """
    Deterministic, explainable scoring.

    Compatibility: aligns with H-024 trust anchors for source authority.
    """
    st = (source_type or "").strip()
    require_approved_source(st)
    authority = float(registry_trust_for(st))
    fresh = _freshness_score(int(freshness_days))

    wf = (workflow_scope or "").strip().lower()
    wf_score = 0.6
    if "procurement" in wf:
        wf_score = 0.82
    elif "graph" in wf:
        wf_score = 0.72
    elif "executive" in wf:
        wf_score = 0.7

    geo_score = 0.35
    if geographic_scope and geographic_scope.strip():
        geo_score = 0.55

    commercial = 0.6 if commercial_relevance is None else _clamp01(float(commercial_relevance))

    weights = {
        "authority": 0.35,
        "freshness": 0.25,
        "workflow": 0.2,
        "geographic": 0.1,
        "commercial": 0.1,
    }
    total = (
        weights["authority"] * authority
        + weights["freshness"] * fresh
        + weights["workflow"] * wf_score
        + weights["geographic"] * geo_score
        + weights["commercial"] * commercial
    )

    return {
        "score": round(_clamp01(total), 4),
        "factors": {
            "source_authority": round(authority, 4),
            "freshness": round(fresh, 4),
            "workflow_relevance": round(wf_score, 4),
            "geographic_relevance": round(geo_score, 4),
            "commercial_relevance": round(commercial, 4),
        },
        "weights": dict(weights),
        "deterministic": True,
    }

