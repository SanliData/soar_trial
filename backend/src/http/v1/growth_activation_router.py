"""
ROUTER: growth_activation_router
PURPOSE: Read-only exposure of Growth & Activation domain (ROL-3 safe)
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter

from src.growth_activation.supply_sources import Supplier, SupplierCategory
from src.growth_activation.geo_targeting_rules import GeoTargetingConfig, GeoTargetingRule
from src.growth_activation.activation_events import LeadCandidate, ActivationDecision
from .growth_activation_endpoints import router as growth_activation_endpoints_router

router = APIRouter(prefix="/growth-activation", tags=["growth-activation"])

***REMOVED*** Include endpoints router
router.include_router(growth_activation_endpoints_router)


@router.get("/health")
def health():
    return {"status": "ok", "domain": "growth_activation"}


@router.get("/sample/supplier")
def sample_supplier():
    """Sample supplier for testing"""
    return Supplier.create(
        supplier_id="sample-001",
        name="Sample Supplier",
        category=SupplierCategory.HVAC,
        address="123 Main St",
        lat=41.0082,
        lon=28.9784,
        phone="+90 555 123 4567",
        email="sample@example.com"
    )


@router.get("/sample/geo-config")
def sample_geo_config():
    """Sample geo targeting config"""
    return GeoTargetingConfig(radius_meters=50.0)


@router.get("/sample/geo-rule")
def sample_geo_rule():
    """Sample geo targeting rule"""
    config = GeoTargetingConfig(radius_meters=50.0)
    return GeoTargetingRule(config)
