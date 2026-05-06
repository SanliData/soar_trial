"""
MODULE: adaptive_centroid_service
PURPOSE: Centroid movement/splitting/pruning reasoning (metadata only) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_adaptive_centroid_movements() -> dict[str, Any]:
    return {
        "centroid_movements": [
            {"cluster_id": "c-01", "movement": "small_shift", "reason": "new procurement docs", "deterministic": True},
            {"cluster_id": "c-02", "movement": "stable", "reason": "low signal change", "deterministic": True},
        ],
        "cluster_splitting": [{"cluster_id": "c-01", "proposal": "split", "reason": "variance drift", "deterministic": True}],
        "cluster_pruning": [{"cluster_id": "c-02", "proposal": "prune", "reason": "low utility", "deterministic": True}],
        "recommendation_only": True,
        "deterministic": True,
        "metadata_only": True,
    }

