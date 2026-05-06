"""
ROUTER: enrichment_router
PURPOSE: API endpoints for compliance-first enrichment settings and consent
ENCODING: UTF-8 WITHOUT BOM
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency
from src.services.enrichment_service import EnrichmentService

router = APIRouter(prefix="/users/me/enrichment", tags=["enrichment"])


***REMOVED*** ============================================================================
***REMOVED*** REQUEST/RESPONSE MODELS
***REMOVED*** ============================================================================

class EnrichmentSettingsRequest(BaseModel):
    email_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum confidence for email enrichment (0.0 to 1.0)")
    phone_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum confidence for phone enrichment (0.0 to 1.0)")
    require_explicit_consent: Optional[bool] = Field(None, description="Require explicit consent before enrichment")
    enable_email_enrichment: Optional[bool] = Field(None, description="Opt-in for email enrichment")
    enable_phone_enrichment: Optional[bool] = Field(None, description="Opt-in for phone enrichment")


class EnrichmentSettingsResponse(BaseModel):
    id: int
    user_id: int
    email_confidence_threshold: float
    phone_confidence_threshold: float
    require_explicit_consent: bool
    consent_given: bool
    consent_given_at: Optional[str]
    enable_email_enrichment: bool
    enable_phone_enrichment: bool
    created_at: str
    updated_at: str


***REMOVED*** ============================================================================
***REMOVED*** ENRICHMENT ENDPOINTS
***REMOVED*** ============================================================================

@router.get("/settings", response_model=EnrichmentSettingsResponse)
async def get_enrichment_settings(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Get enrichment settings for the authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = EnrichmentService(db)
    settings = service.get_or_create_settings(user.id)
    
    return EnrichmentSettingsResponse(**settings.to_dict())


@router.post("/settings", response_model=EnrichmentSettingsResponse)
async def update_enrichment_settings(
    request: EnrichmentSettingsRequest,
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """Update enrichment settings for the authenticated user"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = EnrichmentService(db)
    
    try:
        settings = service.update_settings(
            user_id=user.id,
            email_confidence_threshold=request.email_confidence_threshold,
            phone_confidence_threshold=request.phone_confidence_threshold,
            require_explicit_consent=request.require_explicit_consent,
            enable_email_enrichment=request.enable_email_enrichment,
            enable_phone_enrichment=request.enable_phone_enrichment
        )
        return EnrichmentSettingsResponse(**settings.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/consent", response_model=EnrichmentSettingsResponse)
async def give_enrichment_consent(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Give explicit consent for enrichment.
    This records the user's consent with a timestamp.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = EnrichmentService(db)
    settings = service.give_consent(user.id)
    
    return EnrichmentSettingsResponse(**settings.to_dict())


@router.delete("/consent", response_model=EnrichmentSettingsResponse)
async def revoke_enrichment_consent(
    user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Revoke consent for enrichment.
    This disables all enrichment and clears consent timestamp.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    service = EnrichmentService(db)
    settings = service.revoke_consent(user.id)
    
    return EnrichmentSettingsResponse(**settings.to_dict())
