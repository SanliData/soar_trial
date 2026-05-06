"""
MODULE: relative_scoring_service
PURPOSE: Deterministic relative ranking from explicit metadata facets (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.trajectory_evaluation.trajectory_schema import Trajectory

# Weights sum to 1.0 for the positive linear model; hallucination uses (1 - risk).
_W_CU = 0.25
_W_GC = 0.20
_W_GR = 0.15
_W_SQ = 0.20
_W_HR = 0.20
_VERB_PENALTY = 0.05

_DEFAULT = 0.5


def _f(meta: dict[str, Any], key: str) -> float:
    v = meta.get(key)
    if v is None:
        return _DEFAULT
    try:
        x = float(v)
    except (TypeError, ValueError):
        return _DEFAULT
    return max(0.0, min(1.0, x))


def total_score(trajectory: Trajectory) -> tuple[float, dict[str, float]]:
    """
    Return composite score in [0,1] and per-dimension contribution snapshot.
    All inputs come from reasoning_metadata — no hidden model outputs.
    """
    m = trajectory.reasoning_metadata
    cu = _f(m, "commercial_usefulness")
    gc = _f(m, "graph_consistency")
    gr = _f(m, "geographic_relevance")
    sq = _f(m, "structured_output_quality")
    hr = _f(m, "hallucination_risk")
    verb = _f(m, "verbosity_excess")

    contrib_cu = _W_CU * cu
    contrib_gc = _W_GC * gc
    contrib_gr = _W_GR * gr
    contrib_sq = _W_SQ * sq
    contrib_hr = _W_HR * (1.0 - hr)
    penalty = _VERB_PENALTY * verb

    raw = contrib_cu + contrib_gc + contrib_gr + contrib_sq + contrib_hr - penalty
    score = max(0.0, min(1.0, raw))

    breakdown = {
        "commercial_usefulness": cu,
        "graph_consistency": gc,
        "geographic_relevance": gr,
        "structured_output_quality": sq,
        "hallucination_risk": hr,
        "verbosity_excess": verb,
        "weighted_total": score,
        "contributions": {
            "commercial_usefulness": contrib_cu,
            "graph_consistency": contrib_gc,
            "geographic_relevance": contrib_gr,
            "structured_output_quality": contrib_sq,
            "hallucination_inverse": contrib_hr,
            "verbosity_penalty": penalty,
        },
    }
    return score, breakdown


def rank_trajectories(trajectories: list[Trajectory]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """
    Deterministic sort: by composite score descending, then trajectory_id ascending.
    """
    scored: list[tuple[str, float, dict[str, Any]]] = []
    breakdown_by_id: dict[str, dict[str, Any]] = {}
    for t in trajectories:
        s, bd = total_score(t)
        scored.append((t.trajectory_id, s, bd))
        breakdown_by_id[t.trajectory_id] = bd

    scored.sort(key=lambda x: (-x[1], x[0]))
    ranked_ids = [x[0] for x in scored]
    meta_out: dict[str, dict[str, Any]] = {
        tid: {"score": sc, "breakdown": breakdown_by_id[tid]} for tid, sc, _ in scored
    }
    return ranked_ids, meta_out
