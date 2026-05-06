***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Campaigns Router - Konum bazlı reklam kampanyaları API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from backend.services.b2b import geo_targeting_service
from backend.models.b2b_campaign import Campaign

router = APIRouter(prefix="/api/v1/b2b/campaigns", tags=["B2B"])


class CampaignCreate(BaseModel):
    company_id: int
    target_persona_id: int
    name: str
    description: Optional[str] = None
    ad_title: str
    ad_description: str
    ad_image_url: Optional[str] = None
    ad_landing_url: str
    radius_meters: float = 10.0
    ad_platform: str = "google_ads"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ***REMOVED*** Mobile targeting
    target_device_types: Optional[list] = None
    mobile_only: bool = False
    geofence_polygon: Optional[list] = None
    real_time_tracking: bool = False


@router.post("/", response_model=dict)
async def create_campaign(campaign_data: CampaignCreate):
    """Yeni konum bazlı reklam kampanyası oluştur"""
    try:
        campaign = geo_targeting_service.create_geo_targeted_campaign(
            company_id=campaign_data.company_id,
            target_persona_id=campaign_data.target_persona_id,
            name=campaign_data.name,
            description=campaign_data.description,
            ad_title=campaign_data.ad_title,
            ad_description=campaign_data.ad_description,
            ad_image_url=campaign_data.ad_image_url,
            ad_landing_url=campaign_data.ad_landing_url,
            radius_meters=campaign_data.radius_meters,
            ad_platform=campaign_data.ad_platform,
            start_date=campaign_data.start_date,
            end_date=campaign_data.end_date,
            target_device_types=campaign_data.target_device_types,
            mobile_only=campaign_data.mobile_only,
            geofence_polygon=campaign_data.geofence_polygon,
            real_time_tracking=campaign_data.real_time_tracking
        )
        return campaign.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/for-persona/{persona_id}", response_model=dict)
async def create_campaign_for_persona(
    persona_id: int,
    campaign_name: str,
    ad_title: str,
    ad_description: str,
    ad_landing_url: str,
    radius_meters: float = Query(10.0, ge=1.0, le=1000.0)
):
    """Persona'nın konumuna göre kampanya oluştur"""
    try:
        campaign = geo_targeting_service.create_campaign_for_persona_location(
            persona_id=persona_id,
            campaign_name=campaign_name,
            ad_title=ad_title,
            ad_description=ad_description,
            ad_landing_url=ad_landing_url,
            radius_meters=radius_meters
        )
        if not campaign:
            raise HTTPException(status_code=404, detail="Persona or company location not found")
        return campaign.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/publish", response_model=dict)
async def publish_campaign(campaign_id: int):
    """Kampanyayı reklam platformuna yayınla"""
    try:
        result = geo_targeting_service.publish_campaign_to_platform(campaign_id)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Publish failed"))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}", response_model=dict)
async def get_campaign(campaign_id: int):
    """Kampanya detayı"""
    from backend.services.b2b.geo_targeting_service import geo_targeting_service
    from backend.db import get_db
    from backend.models.b2b_campaign import Campaign
    
    db = next(get_db())
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.to_dict()


@router.get("/location/nearby", response_model=dict)
async def get_nearby_campaigns(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_meters: float = Query(10.0, ge=1.0, le=1000.0)
):
    """Belirli bir konumdaki aktif kampanyaları getir"""
    try:
        campaigns = geo_targeting_service.get_campaigns_by_location(
            latitude=latitude,
            longitude=longitude,
            radius_meters=radius_meters
        )
        return {
            "total": len(campaigns),
            "campaigns": [c.to_dict() for c in campaigns]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{campaign_id}/performance", response_model=dict)
async def update_campaign_performance(
    campaign_id: int,
    impressions: Optional[int] = None,
    clicks: Optional[int] = None,
    conversions: Optional[int] = None,
    cost: Optional[float] = None
):
    """Kampanya performans metriklerini güncelle"""
    campaign = geo_targeting_service.update_campaign_performance(
        campaign_id=campaign_id,
        impressions=impressions,
        clicks=clicks,
        conversions=conversions,
        cost=cost
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign.to_dict()


@router.get("/statistics/{campaign_id}", response_model=dict)
async def get_campaign_statistics(campaign_id: int):
    """Kampanya istatistikleri"""
    stats = geo_targeting_service.get_campaign_statistics(campaign_id=campaign_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return stats


@router.get("/statistics/overview", response_model=dict)
async def get_campaigns_overview():
    """Tüm kampanyaların genel istatistikleri"""
    return geo_targeting_service.get_campaign_statistics()

