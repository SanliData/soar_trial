"""
MODULE: match_request
PURPOSE: Immutable representation of a matching request
ROLE: ROL-3 (pure domain)
ENCODING: UTF-8 WITHOUT BOM
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchRequest:
    requester_id: str
    latitude: float
    longitude: float
    category: str
