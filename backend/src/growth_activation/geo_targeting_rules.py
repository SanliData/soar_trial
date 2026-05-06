"""
FILE: backend/src/growth_activation/geo_targeting_rules.py
PURPOSE: Geo targeting rules for ultra-local radius (20-50m)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Tuple


def meters_between(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lon1 = a
    lat2, lon2 = b
    r = 6371000.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    x = sin(dlat / 2.0) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2.0) ** 2
    return r * (2.0 * asin(sqrt(x)))


@dataclass(frozen=True)
class GeoTargetingConfig:
    radius_meters: float = 50.0
    hard_min_radius_meters: float = 20.0


@dataclass(frozen=True)
class GeoTargetingRule:
    config: GeoTargetingConfig

    def allows(self, supplier_lat: float, supplier_lon: float, target_lat: float, target_lon: float) -> bool:
        d = meters_between((supplier_lat, supplier_lon), (target_lat, target_lon))
        return d <= max(self.config.radius_meters, self.config.hard_min_radius_meters)
