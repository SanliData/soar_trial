"""
MODULE: source_lineage_service
PURPOSE: Source lineage for retrieval results (required) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

LINEAGE_EPOCH = "2026-01-01T00:00:00Z"


def build_source_lineage(
    *,
    source_name: str,
    source_type: str,
    original_reference: str,
    authority_score: float,
    freshness_days: int,
) -> dict[str, Any]:
    sn = (source_name or "").strip()
    st = (source_type or "").strip()
    ref = (original_reference or "").strip()
    if not sn or not st or not ref:
        raise ValueError("invalid lineage fields")
    if authority_score < 0.0 or authority_score > 1.0:
        raise ValueError("invalid authority_score")
    if freshness_days < 0:
        raise ValueError("invalid freshness_days")
    return {
        "source_name": sn,
        "source_type": st,
        "original_reference": ref,
        "authority_score": round(float(authority_score), 4),
        "freshness_days": int(freshness_days),
        "retrieval_timestamp": LINEAGE_EPOCH,
    }

