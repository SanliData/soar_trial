"""
ROUTER: location_affinity_router
PURPOSE: API endpoints for managing location affinity (Location as First-Class Attribute)
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency
from src.services.location_affinity_service import LocationAffinityService
from src.models.persona import Persona

router = APIRouter(prefix="/personas", tags=["location-affinity"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class LocationAffinityRequest(BaseModel):
    latitude: float = Field(..., description="Center latitude")
    longitude: float = Field(..., description="Center longitude")
    location_signals: Optional[List[str]] = Field(None, description="Physical location signals (auto-extracted if not provided)")
    radius_meters: Optional[int] = Field(None, ge=0, description="Radius in meters for circular targeting")
    polygon: Optional[Dict[str, Any]] = Field(None, description="GeoJSON polygon for custom area targeting")
    proximity_clusters: Optional[List[str]] = Field(None, description="List of proximity cluster IDs")


class LocationAffinityResponse(BaseModel):
    persona_id: int
    latitude: float
    longitude: float
    location_affinity_score: Optional[float]
    location_signals: Optional[List[str]]
    location_radius_meters: Optional[int]
    location_polygon: Optional[Dict[str, Any]]
    location_proximity_clusters: Optional[List[str]]


class LocationAffinityScoreRequest(BaseModel):
    target_latitude: float = Field(..., description="Target latitude")
    target_longitude: float = Field(..., description="Target longitude")
    target_signals: Optional[List[str]] = Field(None, description="Target location signals")


class LocationAffinityScoreResponse(BaseModel):
    persona_id: int
    target_latitude: float
    target_longitude: float
    affinity_score: float
    distance_km: Optional[float] = None
    signal_match: Optional[bool] = None


# ============================================================================
# LOCATION AFFINITY ENDPOINTS
# ============================================================================

@router.post("/{persona_id}/location-affinity", response_model=LocationAffinityResponse)
async def set_persona_location_affinity(
    persona_id: int = Path(..., description="Persona ID"),
    request: LocationAffinityRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Set location affinity for a persona.
    Location affinity is a first-class attribute in persona matching.
    
    Supports:
    - Circular targeting (radius_meters)
    - Custom polygon targeting (polygon - GeoJSON format)
    - Physical location signals (urban, coastal, industrial, etc.)
    - Proximity clustering
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify persona belongs to user
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.user_id == user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Validate polygon format if provided
    if request.polygon:
        if not isinstance(request.polygon, dict):
            raise HTTPException(status_code=400, detail="Polygon must be a GeoJSON object")
        if request.polygon.get("type") != "Polygon":
            raise HTTPException(status_code=400, detail="Polygon type must be 'Polygon'")
        if "coordinates" not in request.polygon:
            raise HTTPException(status_code=400, detail="Polygon must have 'coordinates' field")
    
    service = LocationAffinityService(db)
    
    try:
        updated_persona = service.set_location_affinity(
            persona_id=persona_id,
            latitude=request.latitude,
            longitude=request.longitude,
            location_signals=request.location_signals,
            radius_meters=request.radius_meters,
            polygon=request.polygon,
            proximity_clusters=request.proximity_clusters
        )
        
        work_location = updated_persona.work_location or {}
        
        return LocationAffinityResponse(
            persona_id=updated_persona.id,
            latitude=work_location.get("latitude", request.latitude),
            longitude=work_location.get("longitude", request.longitude),
            location_affinity_score=updated_persona.location_affinity_score,
            location_signals=updated_persona.location_signals,
            location_radius_meters=updated_persona.location_radius_meters,
            location_polygon=updated_persona.location_polygon,
            location_proximity_clusters=updated_persona.location_proximity_clusters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{persona_id}/location-affinity", response_model=LocationAffinityResponse)
async def get_persona_location_affinity(
    persona_id: int = Path(..., description="Persona ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get location affinity configuration for a persona"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.user_id == user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    work_location = persona.work_location or {}
    
    return LocationAffinityResponse(
        persona_id=persona.id,
        latitude=work_location.get("latitude", 0.0),
        longitude=work_location.get("longitude", 0.0),
        location_affinity_score=persona.location_affinity_score,
        location_signals=persona.location_signals,
        location_radius_meters=persona.location_radius_meters,
        location_polygon=persona.location_polygon,
        location_proximity_clusters=persona.location_proximity_clusters
    )


@router.post("/{persona_id}/location-affinity/score", response_model=LocationAffinityScoreResponse)
async def calculate_location_affinity_score(
    persona_id: int = Path(..., description="Persona ID"),
    request: LocationAffinityScoreRequest = ...,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Calculate location affinity score between a persona and a target location.
    
    Returns:
    - affinity_score: 0.0 to 1.0 (higher = better match)
    - distance_km: Distance in kilometers
    - signal_match: Whether location signals match
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.user_id == user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    if not persona.work_location:
        raise HTTPException(status_code=400, detail="Persona has no location configured")
    
    service = LocationAffinityService(db)
    
    try:
        affinity_score = service.calculate_affinity_for_target(
            persona_id=persona_id,
            target_latitude=request.target_latitude,
            target_longitude=request.target_longitude,
            target_signals=request.target_signals
        )
        
        # Calculate distance
        persona_lat = persona.work_location.get("latitude")
        persona_lng = persona.work_location.get("longitude")
        distance_km = None
        
        if persona_lat and persona_lng:
            distance_km = service._haversine_distance(
                persona_lat, persona_lng,
                request.target_latitude, request.target_longitude
            )
        
        # Check signal match
        signal_match = None
        if persona.location_signals and request.target_signals:
            matching = set(persona.location_signals) & set(request.target_signals)
            signal_match = len(matching) > 0
        
        return LocationAffinityScoreResponse(
            persona_id=persona_id,
            target_latitude=request.target_latitude,
            target_longitude=request.target_longitude,
            affinity_score=affinity_score,
            distance_km=distance_km,
            signal_match=signal_match
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{persona_id}/location-affinity")
async def remove_persona_location_affinity(
    persona_id: int = Path(..., description="Persona ID"),
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Remove location affinity configuration from a persona"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    persona = db.query(Persona).filter(
        Persona.id == persona_id,
        Persona.user_id == user.id
    ).first()
    
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    # Clear location affinity fields (keep work_location for backward compatibility)
    persona.location_affinity_score = None
    persona.location_signals = None
    persona.location_radius_meters = None
    persona.location_polygon = None
    persona.location_proximity_clusters = None
    
    db.commit()
    
    return {"success": True, "message": "Location affinity removed"}
