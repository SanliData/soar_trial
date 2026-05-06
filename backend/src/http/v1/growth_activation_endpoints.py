"""
FILE: backend/src/http/v1/growth_activation_endpoints.py
PURPOSE: HTTP exposure for Growth & Activation evaluation (read-only)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.growth_activation import (
    Supplier,
    SupplierCategory,
    LeadCandidate,
    decide_activation,
    GeoTargetingConfig,
)

router = APIRouter(prefix="/growth", tags=["growth-activation"])


# -----------------------------
# Request / Response Models
# -----------------------------

class SupplierInput(BaseModel):
    supplier_id: str
    name: str
    category: SupplierCategory
    address: str
    lat: float
    lon: float
    phone: Optional[str] = None
    email: Optional[str] = None


class ActivationRequest(BaseModel):
    supplier: SupplierInput
    target_lat: float = Field(..., description="Target latitude")
    target_lon: float = Field(..., description="Target longitude")
    radius_meters: Optional[float] = Field(
        default=50.0,
        description="Activation radius in meters",
    )
    context: Dict[str, str] = Field(default_factory=dict)


class ActivationResponse(BaseModel):
    status: str
    reason: str
    distance_meters: float
    supplier_id: str


# -----------------------------
# Endpoint
# -----------------------------

@router.post("/evaluate", response_model=ActivationResponse)
def evaluate_activation(payload: ActivationRequest):
    """
    Evaluate whether a supplier is eligible for ultra-local activation.
    Pure evaluation. No side effects.
    """

    try:
        supplier = Supplier.create(
            supplier_id=payload.supplier.supplier_id,
            name=payload.supplier.name,
            category=payload.supplier.category,
            address=payload.supplier.address,
            lat=payload.supplier.lat,
            lon=payload.supplier.lon,
            phone=payload.supplier.phone,
            email=payload.supplier.email,
        )

        candidate = LeadCandidate(
            supplier=supplier,
            target_point=(payload.target_lat, payload.target_lon),
            context=payload.context,
        )

        geo_cfg = GeoTargetingConfig(radius_meters=payload.radius_meters)

        decision = decide_activation(candidate, geo_cfg)

        return ActivationResponse(
            status=decision.status,
            reason=decision.reason,
            distance_meters=decision.distance_meters,
            supplier_id=decision.supplier_id,
        )

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
