"""
MODULE: retrieval_quality_service
PURPOSE: Retrieval quality governance — deterministic ranking checks (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_retrieval_quality(
    *,
    duplicate_ratio: float = 0.0,
    stale_context_ratio: float = 0.0,
    low_authority_ratio: float = 0.0,
    weak_graph_link_ratio: float = 0.0,
    relevance_decay: float = 0.0,
) -> dict[str, Any]:
    d = max(0.0, min(1.0, float(duplicate_ratio)))
    s = max(0.0, min(1.0, float(stale_context_ratio)))
    l = max(0.0, min(1.0, float(low_authority_ratio)))
    w = max(0.0, min(1.0, float(weak_graph_link_ratio)))
    r = max(0.0, min(1.0, float(relevance_decay)))
    quality = round(1.0 - (0.2 * d + 0.25 * s + 0.2 * l + 0.2 * w + 0.15 * r), 4)
    issues = []
    if d > 0.12:
        issues.append("duplicate_retrievals")
    if s > 0.15:
        issues.append("stale_context_retrieval")
    if l > 0.18:
        issues.append("low_authority_retrieval")
    if w > 0.18:
        issues.append("weak_graph_linkage")
    if r > 0.2:
        issues.append("relevance_degradation")
    return {
        "retrieval_quality_score": max(0.0, quality),
        "issues_ranked": issues,
        "component_scores": {
            "duplicate": d,
            "stale_context": s,
            "low_authority": l,
            "weak_graph": w,
            "relevance_decay": r,
        },
        "ranking_rule": "issue_threshold_list_v1",
    }
