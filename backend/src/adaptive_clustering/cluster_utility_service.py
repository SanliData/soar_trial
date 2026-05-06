"""
MODULE: cluster_utility_service
PURPOSE: Explainable cluster utility scoring (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.adaptive_clustering.clustering_validation_service import validate_score01


def score_cluster_utility(*, isolation: float, overlap: float, redundancy: float, retrieval_value: float) -> dict[str, Any]:
    ***REMOVED*** Deterministic explainable formula:
    ***REMOVED*** utility = 0.4*retrieval_value + 0.3*isolation - 0.2*overlap - 0.1*redundancy
    for x in (isolation, overlap, redundancy, retrieval_value):
        validate_score01(float(x))
    utility = 0.4 * retrieval_value + 0.3 * isolation - 0.2 * overlap - 0.1 * redundancy
    utility = max(0.0, min(1.0, utility))
    return {
        "cluster_utility_score": round(utility, 4),
        "isolation_score": round(isolation, 4),
        "overlap_score": round(overlap, 4),
        "redundancy_score": round(redundancy, 4),
        "retrieval_value_score": round(retrieval_value, 4),
        "formula": "0.4*retrieval_value + 0.3*isolation - 0.2*overlap - 0.1*redundancy",
        "deterministic": True,
        "explainable": True,
    }


def export_cluster_utility() -> dict[str, Any]:
    rows = [
        {"cluster_id": "c-01", "utility": score_cluster_utility(isolation=0.7, overlap=0.2, redundancy=0.1, retrieval_value=0.8)},
        {"cluster_id": "c-02", "utility": score_cluster_utility(isolation=0.5, overlap=0.4, redundancy=0.3, retrieval_value=0.4)},
    ]
    return {"clusters": rows, "deterministic": True}

