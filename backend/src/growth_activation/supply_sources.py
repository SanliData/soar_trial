"""
FILE: backend/src/growth_activation/supply_sources.py
PURPOSE: Supplier sourcing and normalization
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SupplierCategory(str, Enum):
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    GENERAL_REPAIR = "general_repair"


@dataclass(frozen=True)
class Supplier:
    supplier_id: str
    name: str
    category: SupplierCategory
    address: str
    lat: float
    lon: float
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None

    @staticmethod
    def create(
        supplier_id: str,
        name: str,
        category: SupplierCategory,
        address: str,
        lat: float,
        lon: float,
        phone: Optional[str] = None,
        website: Optional[str] = None,
        email: Optional[str] = None,
    ) -> "Supplier":
        return Supplier(
            supplier_id=supplier_id,
            name=name,
            category=category,
            address=address,
            lat=lat,
            lon=lon,
            phone=phone,
            website=website,
            email=email,
        )

    def is_contactable(self) -> bool:
        return bool(self.phone or self.website or self.email)
