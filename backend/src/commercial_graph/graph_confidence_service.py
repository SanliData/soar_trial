"""
MODULE: graph_confidence_service
PURPOSE: Deterministic relationship confidence scoring (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.commercial_graph.entity_schema import CommercialEntity

WEIGHT_AUTHORITY = 0.35
WEIGHT_FRESHNESS = 0.25
WEIGHT_EVIDENCE = 0.25
WEIGHT_CROSS_SOURCE = 0.15


def _freshness_factor(freshness_days: int) -> float:
    if freshness_days <= 0:
        return 1.0
    return max(0.15, 1.0 - min(freshness_days, 730) / 730.0)


def _evidence_factor(evidence_sources: list[str]) -> tuple[float, int]:
    n = len({e.strip() for e in evidence_sources if e.strip()})
    ***REMOVED*** Diminishing returns after 3 distinct sources
    base = min(1.0, 0.35 + n * 0.22)
    return round(base, 4), n


def _cross_source_bonus(source_a: CommercialEntity, source_b: CommercialEntity) -> float:
    ta = set(source_a.tags)
    tb = set(source_b.tags)
    overlap = len(ta & tb)
    return min(1.0, 0.45 + overlap * 0.12)


def compute_relationship_confidence(
    *,
    source: CommercialEntity,
    target: CommercialEntity,
    relationship_type: str,
    evidence_sources: list[str],
    repetition_count: int,
) -> float:
    """
    repetition_count: how many parallel evidences already recorded for same triple pattern (foundation uses 0).
    """
    _ = relationship_type  ***REMOVED*** reserved for future typed priors
    auth = (source.authority_score + target.authority_score) / 2.0
    fresh = (_freshness_factor(source.freshness_days) + _freshness_factor(target.freshness_days)) / 2.0
    ev_score, n_ev = _evidence_factor(evidence_sources)
    cross = _cross_source_bonus(source, target)
    rep_boost = min(0.15, repetition_count * 0.03)
    raw = (
        WEIGHT_AUTHORITY * auth
        + WEIGHT_FRESHNESS * fresh
        + WEIGHT_EVIDENCE * ev_score
        + WEIGHT_CROSS_SOURCE * cross
        + rep_boost
    )
    conf = min(1.0, max(0.0, raw))
    if n_ev == 0:
        conf *= 0.65
    return round(conf, 4)


def explain_confidence_factors(
    *,
    source: CommercialEntity,
    target: CommercialEntity,
    evidence_sources: list[str],
    repetition_count: int,
) -> dict[str, float]:
    auth = (source.authority_score + target.authority_score) / 2.0
    fresh = (_freshness_factor(source.freshness_days) + _freshness_factor(target.freshness_days)) / 2.0
    ev_score, n_ev = _evidence_factor(evidence_sources)
    cross = _cross_source_bonus(source, target)
    return {
        "authority_blend": round(auth, 4),
        "freshness_blend": round(fresh, 4),
        "evidence_strength": round(ev_score, 4),
        "tag_overlap_signal": round(cross, 4),
        "distinct_evidence_count": float(n_ev),
        "repetition_boost": float(min(0.15, repetition_count * 0.03)),
        "no_evidence_penalty_applies": 1.0 if n_ev == 0 else 0.0,
    }
