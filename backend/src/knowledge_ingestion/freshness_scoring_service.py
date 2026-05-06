"""
MODULE: freshness_scoring_service
PURPOSE: Deterministic freshness confidence and stale flags (H-024)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

***REMOVED*** Beyond this age, content is treated as stale for policy and ranking (foundation defaults).
STALE_THRESHOLD_DAYS = 180
STALE_CONFIDENCE_FLOOR = 0.15


def freshness_confidence_score(freshness_days: int) -> float:
    """
    Returns 0..1 where higher means more temporally reliable for retrieval ranking.
    Linear decay toward a floor; fully deterministic.
    """
    if freshness_days <= 0:
        return 1.0
    if freshness_days >= 730:
        return STALE_CONFIDENCE_FLOOR
    ***REMOVED*** Gentle decay: ~0.75 at 180d
    step = (1.0 - STALE_CONFIDENCE_FLOOR) / 730.0
    return round(max(STALE_CONFIDENCE_FLOOR, 1.0 - freshness_days * step), 4)


def is_stale_record(freshness_days: int) -> bool:
    return freshness_days > STALE_THRESHOLD_DAYS


def freshness_summary(freshness_days: int) -> dict[str, object]:
    return {
        "freshness_days": freshness_days,
        "freshness_confidence": freshness_confidence_score(freshness_days),
        "is_stale": is_stale_record(freshness_days),
        "stale_threshold_days": STALE_THRESHOLD_DAYS,
    }
