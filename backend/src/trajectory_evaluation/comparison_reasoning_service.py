"""
MODULE: comparison_reasoning_service
PURPOSE: Template-based comparison explanations — deterministic only (H-028)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_DIM_LABELS = {
    "commercial_usefulness": "commercial usefulness",
    "graph_consistency": "graph consistency",
    "geographic_relevance": "geographic relevance",
    "structured_output_quality": "structured output quality",
    "hallucination_risk": "hallucination risk (lower is better)",
}

_EPS = 0.02


def _winner_reason(w_dim: float, l_dim: float, key: str) -> str | None:
    label = _DIM_LABELS.get(key, key)
    if key == "hallucination_risk":
        if l_dim - w_dim > _EPS:
            return f"lower hallucination risk than alternative ({label})"
        return None
    if w_dim - l_dim > _EPS:
        return f"stronger {label}"
    return None


def build_pairwise_summary(
    _winner_id: str,
    loser_id: str,
    winner_breakdown: dict[str, Any],
    loser_breakdown: dict[str, Any],
) -> list[str]:
    lines: list[str] = []
    ***REMOVED*** Compare raw dimension values stored at top level of breakdown
    w_top = {k: winner_breakdown.get(k) for k in _DIM_LABELS}
    l_top = {k: loser_breakdown.get(k) for k in _DIM_LABELS}
    for key in _DIM_LABELS:
        try:
            wv = float(w_top.get(key, 0.5))
            lv = float(l_top.get(key, 0.5))
        except (TypeError, ValueError):
            continue
        reason = _winner_reason(wv, lv, key)
        if reason:
            lines.append(reason)
    if not lines:
        lines.append("higher weighted composite score under deterministic policy (tie-break by trajectory id)")
    return lines


def build_evaluation_narrative(
    ranked_ids: list[str],
    score_meta: dict[str, dict[str, Any]],
) -> str:
    """
    Produce a bounded audit string: winner headline plus pairwise bullets vs next-ranked only
    (keeps output short; full matrices deferred to telemetry).
    """
    if not ranked_ids:
        return ""
    winner = ranked_ids[0]
    parts: list[str] = [f"Winner: {winner} (deterministic relative score)."]
    if len(ranked_ids) >= 2:
        loser = ranked_ids[1]
        wbd = score_meta.get(winner, {}).get("breakdown") or {}
        lbd = score_meta.get(loser, {}).get("breakdown") or {}
        pairs = build_pairwise_summary(winner, loser, wbd, lbd)
        for p in pairs[:6]:
            parts.append(f"- Compared to {loser}: {p}.")
    return "\n".join(parts)
