"""
FILE: backend/src/growth_activation/activation_events.py
PURPOSE: Lead activation decisions (pure logic)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .geo_targeting_rules import GeoTargetingConfig, GeoTargetingRule, meters_between
from .supply_sources import Supplier


@dataclass(frozen=True)
class LeadCandidate:
    supplier: Supplier
    target_point: Tuple[float, float]
    context: Dict[str, str]


@dataclass(frozen=True)
class ActivationDecision:
    status: str
    reason: str
    distance_meters: float
    supplier_id: str


def decide_activation(
    candidate: LeadCandidate,
    geo_cfg: Optional[GeoTargetingConfig] = None,
    require_contactable: bool = True,
) -> ActivationDecision:
    cfg = geo_cfg or GeoTargetingConfig()
    rule = GeoTargetingRule(cfg)

    s = candidate.supplier
    tlat, tlon = candidate.target_point
    d = meters_between((s.lat, s.lon), (tlat, tlon))

    if require_contactable and not s.is_contactable():
        return ActivationDecision("rejected", "not_contactable", d, s.supplier_id)

    if not rule.allows(s.lat, s.lon, tlat, tlon):
        return ActivationDecision("rejected", "outside_radius", d, s.supplier_id)

    return ActivationDecision("eligible", "within_radius", d, s.supplier_id)
