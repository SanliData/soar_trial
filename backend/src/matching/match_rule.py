"""
MODULE: match_rule
PURPOSE: Deterministic matching rule definition
ROLE: ROL-3 (pure logic)
ENCODING: UTF-8 WITHOUT BOM
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class MatchRule:
    max_distance_meters: int
    category: str
