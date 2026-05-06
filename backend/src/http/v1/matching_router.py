"""
ROUTER: matching_router
PURPOSE: Read-only exposure of Matching domain (sample only)
ROLE: ROL-3 safe router
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter
from typing import List

from src.matching.match_request import MatchRequest
from src.matching.match_rule import MatchRule
from src.matching.match_engine import apply_rule

router = APIRouter(prefix="/matching", tags=["matching"])



@router.get("/health")
def health():
    return {
        "status": "ok",
        "domain": "matching"
    }


@router.get("/sample")
def sample_match():
    request = MatchRequest(
        requester_id="req-1",
        latitude=0.0,
        longitude=0.0,
        category="plumber"
    )

    rule = MatchRule(
        max_distance_meters=100,
        category="plumber"
    )

    supply_points: List[tuple] = [
        ("sup-1", 0.0, 0.0, "plumber"),
        ("sup-2", 1.0, 1.0, "plumber"),
        ("sup-3", 0.0, 0.0, "electrician"),
    ]

    result = apply_rule(
        request=request,
        rule=rule,
        supply_points=supply_points
    )

    return {
        "request_id": result.request_id,
        "matched_supply_ids": result.matched_supply_ids
    }
