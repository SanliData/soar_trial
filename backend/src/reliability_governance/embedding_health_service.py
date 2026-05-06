"""
MODULE: embedding_health_service
PURPOSE: Embedding freshness and coverage scoring — no mutation (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_embedding_health(
    *,
    stale_ratio: float = 0.0,
    missing_ratio: float = 0.0,
    low_confidence_ratio: float = 0.0,
    max_age_hours: float = 0.0,
    invalid_source_ratio: float = 0.0,
) -> dict[str, Any]:
    stale_r = max(0.0, min(1.0, float(stale_ratio)))
    miss_r = max(0.0, min(1.0, float(missing_ratio)))
    low_r = max(0.0, min(1.0, float(low_confidence_ratio)))
    inv_r = max(0.0, min(1.0, float(invalid_source_ratio)))
    age = max(0.0, float(max_age_hours))
    age_pressure = min(1.0, age / 720.0)   # 30d horizon
    health = round(
        1.0 - (0.25 * stale_r + 0.25 * miss_r + 0.2 * low_r + 0.15 * inv_r + 0.15 * age_pressure),
        4,
    )
    return {
        "embedding_health_score": max(0.0, health),
        "flags": {
            "stale_embeddings": stale_r > 0.15,
            "missing_embeddings": miss_r > 0.1,
            "low_confidence_embeddings": low_r > 0.2,
            "embedding_age_elevated": age > 168.0,
            "invalid_source_ratio_elevated": inv_r > 0.05,
        },
        "inputs_echo": {
            "max_age_hours": age,
            "stale_ratio": stale_r,
            "missing_ratio": miss_r,
        },
        "scoring_rule": "weighted_health_v1",
        "mutation_note": "scores_only_no_embedding_writes",
    }
