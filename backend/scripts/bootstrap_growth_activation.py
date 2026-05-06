"""
BOOTSTRAP SCRIPT
PURPOSE: One-time generation of Growth & Activation core modules
SCOPE: ROL-3 implementation only
ENCODING: UTF-8 WITHOUT BOM
IDEMPOTENCY: Overwrites target files intentionally
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
TARGET_DIR = BASE_DIR / "src" / "growth_activation"

TARGET_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "supply_sources.py": """\
\"\"\"
MODULE: supply_sources
PURPOSE: Define technician supply acquisition sources (pure definitions)
\"\"\"

from dataclasses import dataclass
from typing import Literal


SupplySourceType = Literal[
    "organic_signup",
    "referral",
    "partner_import",
    "field_campaign"
]


@dataclass(frozen=True)
class SupplySource:
    source_type: SupplySourceType
    description: str
""",

    "geo_targeting_rules.py": """\
\"\"\"
MODULE: geo_targeting_rules
PURPOSE: Geo-targeting constraints for activation logic
\"\"\"

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class GeoTargetRule:
    center_lat: float
    center_lng: float
    radius_meters: int

    def contains(self, lat: float, lng: float) -> bool:
        return self._distance_meters(lat, lng) <= self.radius_meters

    def _distance_meters(self, lat: float, lng: float) -> float:
        ***REMOVED*** Haversine (approximate, deterministic)
        from math import radians, cos, sin, sqrt, atan2

        R = 6371000
        dlat = radians(lat - self.center_lat)
        dlng = radians(lng - self.center_lng)

        a = (
            sin(dlat / 2) ** 2
            + cos(radians(self.center_lat))
            * cos(radians(lat))
            * sin(dlng / 2) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c
""",

    "activation_events.py": """\
\"\"\"
MODULE: activation_events
PURPOSE: Define activation event payloads (no side effects)
\"\"\"

from dataclasses import dataclass
from datetime import datetime
from typing import Literal


ActivationEventType = Literal[
    "supply_registered",
    "geo_matched",
    "activated"
]


@dataclass(frozen=True)
class ActivationEvent:
    event_type: ActivationEventType
    occurred_at: datetime
    entity_id: str
    metadata: dict
"""
}

for filename, content in FILES.items():
    path = TARGET_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"CREATED: {path.relative_to(BASE_DIR)}")
