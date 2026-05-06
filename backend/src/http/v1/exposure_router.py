"""
ROUTER: exposure_router
PURPOSE: Precision exposure and conversion tracking API endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.models.precision_exposure import PrecisionExposure
from src.models.exposure_conversion import ExposureConversion
from src.models.access_gate import AccessGate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exposure", tags=["exposure"])


class PrecisionExposureRequest(BaseModel):
    """Request model for creating precision exposure campaign"""
    feasibility_report_id: Optional[int] = None
    campaign_name: str = Field(..., description="Campaign name")
    target_geography: Optional[str] = None
    target_roles: Optional[str] = None
    target_industry: Optional[str] = None
    location_coordinates: Optional[dict] = None  ***REMOVED*** {"lat": 41.0082, "lng": 28.9784}
    location_radius_meters: Optional[int] = None
    location_polygon: Optional[dict] = None  ***REMOVED*** GeoJSON polygon
    management_type: str = Field("soar_managed", description="soar_managed, partner_managed, customer_agency")
    target_context: Optional[dict] = None  ***REMOVED*** Contextual targeting (no PII)


class ConversionTrackingRequest(BaseModel):
    """Request model for tracking conversion events (impressions, clicks, views)"""
    precision_exposure_id: int
    event_type: str = Field(..., description="impression, click, content_view")
    event_context: Optional[dict] = None  ***REMOVED*** Contextual data only (no PII)


@router.post("/create")
async def create_precision_exposure(
    request: PrecisionExposureRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Create precision exposure campaign.
    Targets by location + persona context, NOT by individual identifiers.
    No personal data until explicit outreach stage.
    """
    try:
        ***REMOVED*** Check access gate for exposure module
        access_gate = db.query(AccessGate).filter(
            AccessGate.user_id == user_id,
            AccessGate.module_type == "exposure"
        ).first()
        
        if not access_gate or not access_gate.is_unlocked:
            raise HTTPException(
                status_code=403,
                detail="Precision exposure module requires purchase. Please unlock access first."
            )
        
        ***REMOVED*** Create precision exposure campaign
        exposure = PrecisionExposure(
            user_id=user_id,
            feasibility_report_id=request.feasibility_report_id,
            campaign_name=request.campaign_name,
            target_geography=request.target_geography,
            target_roles=request.target_roles,
            target_industry=request.target_industry,
            location_coordinates=request.location_coordinates,
            location_radius_meters=request.location_radius_meters,
            location_polygon=request.location_polygon,
            management_type=request.management_type,
            status="draft",
            target_context=request.target_context
        )
        
        db.add(exposure)
        db.commit()
        db.refresh(exposure)
        
        logger.info(f"Precision exposure created: {exposure.id} (user_id: {user_id}, campaign: {request.campaign_name})")
        
        return {
            "success": True,
            "exposure": exposure.to_dict(),
            "message": "Precision exposure campaign created"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating precision exposure: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating precision exposure: {str(e)}")


@router.post("/track-conversion")
async def track_conversion(
    request: ConversionTrackingRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Track soft conversion events (impressions, clicks, views).
    NO lead labeling at this stage - only interest signals.
    """
    try:
        ***REMOVED*** Get or create conversion tracking record
        conversion = db.query(ExposureConversion).filter(
            ExposureConversion.user_id == user_id,
            ExposureConversion.precision_exposure_id == request.precision_exposure_id,
            ExposureConversion.event_type == request.event_type
        ).first()
        
        if not conversion:
            ***REMOVED*** Create new conversion tracking
            conversion = ExposureConversion(
                user_id=user_id,
                precision_exposure_id=request.precision_exposure_id,
                event_type=request.event_type,
                event_context=request.event_context,
                impression_count=1 if request.event_type == "impression" else 0,
                click_count=1 if request.event_type == "click" else 0,
                content_view_count=1 if request.event_type == "content_view" else 0,
                interest_score=10 if request.event_type == "click" else 5  ***REMOVED*** Soft interest scoring
            )
            db.add(conversion)
        else:
            ***REMOVED*** Update existing conversion tracking
            if request.event_type == "impression":
                conversion.impression_count += 1
            elif request.event_type == "click":
                conversion.click_count += 1
                conversion.interest_score = min(100, conversion.interest_score + 10)
            elif request.event_type == "content_view":
                conversion.content_view_count += 1
                conversion.interest_score = min(100, conversion.interest_score + 5)
            
            conversion.last_event_at = datetime.utcnow()
            if request.event_context:
                ***REMOVED*** Update context (merge, don't replace)
                if conversion.event_context:
                    conversion.event_context.update(request.event_context)
                else:
                    conversion.event_context = request.event_context
        
        db.commit()
        db.refresh(conversion)
        
        logger.debug(f"Conversion tracked: {request.event_type} (exposure_id: {request.precision_exposure_id}, user_id: {user_id})")
        
        return {
            "success": True,
            "conversion": conversion.to_dict(),
            "message": f"Conversion tracked: {request.event_type}"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error tracking conversion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error tracking conversion: {str(e)}")


@router.get("/conversions/{exposure_id}")
async def get_conversion_stats(
    exposure_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get conversion statistics for precision exposure campaign.
    Returns aggregated metrics only - no personal identifiers.
    """
    try:
        conversions = db.query(ExposureConversion).filter(
            ExposureConversion.user_id == user_id,
            ExposureConversion.precision_exposure_id == exposure_id
        ).all()
        
        if not conversions:
            return {
                "success": True,
                "exposure_id": exposure_id,
                "total_impressions": 0,
                "total_clicks": 0,
                "total_content_views": 0,
                "average_interest_score": 0,
                "conversions": []
            }
        
        ***REMOVED*** Aggregate metrics
        total_impressions = sum(c.impression_count for c in conversions)
        total_clicks = sum(c.click_count for c in conversions)
        total_content_views = sum(c.content_view_count for c in conversions)
        avg_interest_score = sum(c.interest_score for c in conversions) / len(conversions) if conversions else 0
        
        return {
            "success": True,
            "exposure_id": exposure_id,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_content_views": total_content_views,
            "average_interest_score": round(avg_interest_score, 2),
            "conversions": [c.to_dict() for c in conversions]
        }
        
    except Exception as e:
        logger.error(f"Error getting conversion stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting conversion stats: {str(e)}")
