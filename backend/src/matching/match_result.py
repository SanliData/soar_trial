"""
MODULE: match_result
PURPOSE: Immutable matching outcome
ROLE: ROL-3 (pure domain)
ENCODING: UTF-8 WITHOUT BOM
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class MatchResult:
    request_id: str
    matched_supply_ids: List[str]
