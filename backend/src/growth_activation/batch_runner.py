"""
FILE: backend/src/growth_activation/batch_runner.py
PURPOSE: Batch evaluation of suppliers for ultra-local activation
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import List, Tuple

from .supply_sources import Supplier, SupplierCategory
from .activation_events import LeadCandidate, decide_activation
from .geo_targeting_rules import GeoTargetingConfig


***REMOVED*** Dallas Fort Worth reference point (demo)
DFW_CENTER: Tuple[float, float] = (32.7767, -96.7970)


def load_demo_suppliers() -> List[Supplier]:
    """
    Temporary demo loader.
    This will be replaced by real ingestion (Maps, directories, CRM).
    """
    return [
        Supplier.create(
            supplier_id="dfw-hvac-001",
            name="Dallas HVAC Pro",
            category=SupplierCategory.HVAC,
            address="Dallas, TX",
            lat=32.7767,
            lon=-96.7970,
            phone="(214) 555-1001",
        ),
        Supplier.create(
            supplier_id="dfw-plumb-002",
            name="Plano Plumbing",
            category=SupplierCategory.PLUMBING,
            address="Plano, TX",
            lat=33.0198,
            lon=-96.6989,
            phone=None,
        ),
    ]


def run_batch():
    """
    Evaluate all suppliers against a single target point.
    Pure logic, no side effects.
    """
    suppliers = load_demo_suppliers()
    geo_cfg = GeoTargetingConfig(radius_meters=50.0)

    results = []

    for supplier in suppliers:
        candidate = LeadCandidate(
            supplier=supplier,
            target_point=DFW_CENTER,
            context={"market": "DFW"},
        )
        decision = decide_activation(candidate, geo_cfg)
        results.append(decision)

    return results


if __name__ == "__main__":
    decisions = run_batch()
    for decision in decisions:
        print(
            f"{decision.supplier_id} | "
            f"{decision.status} | "
            f"{decision.reason} | "
            f"{int(decision.distance_meters)}m"
        )
