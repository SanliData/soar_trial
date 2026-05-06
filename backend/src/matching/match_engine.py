"""
MODULE: match_engine
PURPOSE: Core deterministic matching logic
ROLE: ROL-3 (pure computation)
ENCODING: UTF-8 WITHOUT BOM
"""

from math import radians, cos, sin, sqrt, atan2
from typing import List

from src.matching.match_request import MatchRequest
from src.matching.match_rule import MatchRule
from src.matching.match_result import MatchResult


def _distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Haversine formula (deterministic)
    r = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def apply_rule(
    request: MatchRequest,
    rule: MatchRule,
    supply_points: List[tuple],
) -> MatchResult:
    """
    supply_points: List of tuples -> (supply_id, lat, lon, category)
    """
    matched_ids: List[str] = []

    for supply_id, lat, lon, category in supply_points:
        if category != rule.category:
            continue

        distance = _distance_meters(
            request.latitude,
            request.longitude,
            lat,
            lon,
        )

        if distance <= rule.max_distance_meters:
            matched_ids.append(supply_id)

    return MatchResult(
        request_id=request.requester_id,
        matched_supply_ids=matched_ids,
    )
