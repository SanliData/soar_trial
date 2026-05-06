***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Mobile Targeting Router - Mobile device location-based targeting API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from backend.services.b2b import mobile_geo_targeting_service, geo_targeting_service

router = APIRouter(prefix="/api/v1/b2b/mobile-targeting", tags=["B2B"])


class MobileLocationCheck(BaseModel):
    campaign_id: int
    latitude: float
    longitude: float
    device_type: str = "mobile"  ***REMOVED*** mobile, tablet, desktop


class MobileLocationQuery(BaseModel):
    latitude: float
    longitude: float
    device_type: str = "mobile"
    radius_meters: Optional[float] = None


class MobileLocationTrack(BaseModel):
    campaign_id: int
    latitude: float
    longitude: float
    device_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class MobileCampaignCreate(BaseModel):
    company_id: int
    target_persona_id: int
    name: str
    ad_title: str
    ad_description: str
    ad_landing_url: str
    target_latitude: float
    target_longitude: float
    radius_meters: float = 10.0
    mobile_only: bool = True
    geofence_polygon: Optional[list] = None
    real_time_tracking: bool = False


@router.post("/check-location", response_model=dict)
async def check_mobile_location_for_campaign(check_data: MobileLocationCheck):
    """Check if mobile device location matches campaign targeting"""
    try:
        result = mobile_geo_targeting_service.check_mobile_location_for_campaign(
            campaign_id=check_data.campaign_id,
            mobile_latitude=check_data.latitude,
            mobile_longitude=check_data.longitude,
            device_type=check_data.device_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/get-campaigns", response_model=dict)
async def get_campaigns_for_mobile_location(query_data: MobileLocationQuery):
    """Get all campaigns that should be shown for mobile device at given location"""
    try:
        campaigns = mobile_geo_targeting_service.get_campaigns_for_mobile_location(
            mobile_latitude=query_data.latitude,
            mobile_longitude=query_data.longitude,
            device_type=query_data.device_type,
            radius_meters=query_data.radius_meters
        )
        return {
            "total": len(campaigns),
            "campaigns": campaigns
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/track-location", response_model=dict)
async def track_mobile_location(track_data: MobileLocationTrack):
    """Track mobile device location for real-time targeting"""
    try:
        result = mobile_geo_targeting_service.track_mobile_location(
            campaign_id=track_data.campaign_id,
            mobile_latitude=track_data.latitude,
            mobile_longitude=track_data.longitude,
            device_id=track_data.device_id,
            timestamp=track_data.timestamp
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create-mobile-campaign", response_model=dict)
async def create_mobile_campaign(campaign_data: MobileCampaignCreate):
    """Create mobile-specific geo-targeted campaign"""
    try:
        campaign = mobile_geo_targeting_service.create_mobile_geo_campaign(
            company_id=campaign_data.company_id,
            target_persona_id=campaign_data.target_persona_id,
            name=campaign_data.name,
            ad_title=campaign_data.ad_title,
            ad_description=campaign_data.ad_description,
            ad_landing_url=campaign_data.ad_landing_url,
            target_latitude=campaign_data.target_latitude,
            target_longitude=campaign_data.target_longitude,
            radius_meters=campaign_data.radius_meters,
            mobile_only=campaign_data.mobile_only,
            geofence_polygon=campaign_data.geofence_polygon,
            real_time_tracking=campaign_data.real_time_tracking
        )
        return campaign.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/nearby", response_model=dict)
async def get_nearby_campaigns(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    device_type: str = Query("mobile", regex="^(mobile|tablet|desktop)$"),
    radius_meters: Optional[float] = Query(None, ge=1.0, le=10000.0)
):
    """Get nearby campaigns for mobile device (simplified endpoint)"""
    try:
        campaigns = mobile_geo_targeting_service.get_campaigns_for_mobile_location(
            mobile_latitude=latitude,
            mobile_longitude=longitude,
            device_type=device_type,
            radius_meters=radius_meters
        )
        return {
            "total": len(campaigns),
            "campaigns": campaigns
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

