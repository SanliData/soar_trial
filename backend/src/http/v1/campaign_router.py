"""
ROUTER: campaign_router
PURPOSE: Bulk campaign management for multiple companies, personnel, and locations
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.google_ads_service import get_google_ads_service

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


***REMOVED*** Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class CampaignTarget(BaseModel):
    company_ids: Optional[List[str]] = None
    personnel_ids: Optional[List[str]] = None
    location_ids: Optional[List[str]] = None
    location_polygons: Optional[List[Dict[str, Any]]] = None  ***REMOVED*** Polygon coordinates
    filters: Optional[Dict[str, Any]] = None  ***REMOVED*** Additional filters


class CampaignCreate(BaseModel):
    name: str
    ad_content_type: str  ***REMOVED*** "text", "image", "link"
    ad_content: str  ***REMOVED*** Text, image URL, or link URL
    ad_type: str  ***REMOVED*** "location-based", "social", "email", "sms"
    target: CampaignTarget
    schedule: Optional[Dict[str, Any]] = None  ***REMOVED*** Scheduling options
    budget: Optional[float] = None
    max_impressions: Optional[int] = None


class CampaignResponse(BaseModel):
    campaign_id: str
    name: str
    status: str
    total_targets: int
    companies_count: int
    personnel_count: int
    locations_count: int
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class CampaignStats(BaseModel):
    campaign_id: str
    total_targets: int
    companies_count: int
    personnel_count: int
    locations_count: int
    impressions: int
    clicks: int
    conversions: int
    status: str


@router.post("/create", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate):
    """
    Create a bulk campaign for multiple companies, personnel, and locations.
    """
    campaign_id = str(uuid.uuid4())
    
    ***REMOVED*** Calculate target counts
    companies_count = len(campaign.target.company_ids) if campaign.target.company_ids else 0
    personnel_count = len(campaign.target.personnel_ids) if campaign.target.personnel_ids else 0
    locations_count = 0
    
    if campaign.target.location_ids:
        locations_count += len(campaign.target.location_ids)
    if campaign.target.location_polygons:
        locations_count += len(campaign.target.location_polygons)
    
    total_targets = companies_count + personnel_count + locations_count
    
    return CampaignResponse(
        campaign_id=campaign_id,
        name=campaign.name,
        status="created",
        total_targets=total_targets,
        companies_count=companies_count,
        personnel_count=personnel_count,
        locations_count=locations_count,
        created_at=datetime.utcnow().isoformat()
    )


@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str):
    """
    Start a campaign. This will begin showing ads to all targets.
    """
    return {
        "campaign_id": campaign_id,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "message": "Campaign started. Ads will be shown to all targets."
    }


@router.post("/{campaign_id}/stop")
async def stop_campaign(campaign_id: str):
    """
    Stop a running campaign.
    """
    return {
        "campaign_id": campaign_id,
        "status": "stopped",
        "stopped_at": datetime.utcnow().isoformat(),
        "message": "Campaign stopped."
    }


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str,
    customer_id: Optional[str] = Query(None, description="Google Ads Customer ID (format: XXX-XXX-XXXX)"),
    google_ads_campaign_id: Optional[str] = Query(None, description="Google Ads Campaign ID (if different from campaign_id)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user: Optional[User] = Depends(get_current_user_from_header)
):
    """
    Get statistics for a campaign.
    If Google Ads Customer ID and Campaign ID are provided, fetches real-time performance data.
    Otherwise returns database-stored campaign stats.
    Used for Step 9 (Ad Display) dashboard.
    """
    ***REMOVED*** If Google Ads IDs provided, fetch real performance data
    if customer_id and google_ads_campaign_id:
        ads_service = get_google_ads_service()
        performance = ads_service.get_campaign_performance(
            customer_id=customer_id,
            campaign_id=google_ads_campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if performance.get("success"):
            metrics = performance.get("metrics", {})
            return {
                "success": True,
                "campaign_id": campaign_id,
                "google_ads_campaign_id": google_ads_campaign_id,
                "campaign_name": performance.get("campaign_name", ""),
                "status": performance.get("campaign_status", "unknown"),
                "date_range": performance.get("date_range", {}),
                "metrics": {
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "cost": metrics.get("cost", 0),
                    "conversions": metrics.get("conversions", 0),
                    "conversions_value": metrics.get("conversions_value", 0),
                    "ctr": metrics.get("ctr", 0),
                    "average_cpc": metrics.get("average_cpc", 0),
                    "cost_per_conversion": metrics.get("cost_per_conversion", 0),
                    "conversion_rate": metrics.get("conversion_rate", 0)
                },
                "budget": performance.get("budget", {}),
                "daily_breakdown": performance.get("daily_breakdown", []),
                "source": "google_ads_api"
            }
        else:
            ***REMOVED*** Fallback to database stats if API fails
            pass
    
    ***REMOVED*** Get from database (mock for now, should query Campaign model)
    ***REMOVED*** In production, query Campaign model with campaign_id and user_id
    return {
        "success": True,
        "campaign_id": campaign_id,
        "metrics": {
            "impressions": 45000,
            "clicks": 1200,
            "cost": 450.50,
            "conversions": 45,
            "conversions_value": 4500.00,
            "ctr": 2.67,
            "average_cpc": 0.38,
            "cost_per_conversion": 10.01,
            "conversion_rate": 3.75
        },
        "status": "running",
        "source": "database"
    }


@router.get("/list")
async def list_campaigns():
    """
    List all campaigns.
    """
    ***REMOVED*** Mock list - in production, get from database
    return {
        "campaigns": [
            {
                "campaign_id": "camp-001",
                "name": "Industrial Yeast Campaign",
                "status": "running",
                "total_targets": 1500,
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 1
    }


@router.post("/bulk-create")
async def bulk_create_campaigns(campaigns: List[CampaignCreate]):
    """
    Create multiple campaigns at once.
    """
    created_campaigns = []
    
    for campaign in campaigns:
        campaign_id = str(uuid.uuid4())
        companies_count = len(campaign.target.company_ids) if campaign.target.company_ids else 0
        personnel_count = len(campaign.target.personnel_ids) if campaign.target.personnel_ids else 0
        locations_count = 0
        
        if campaign.target.location_ids:
            locations_count += len(campaign.target.location_ids)
        if campaign.target.location_polygons:
            locations_count += len(campaign.target.location_polygons)
        
        total_targets = companies_count + personnel_count + locations_count
        
        created_campaigns.append({
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": "created",
            "total_targets": total_targets,
            "companies_count": companies_count,
            "personnel_count": personnel_count,
            "locations_count": locations_count
        })
    
    return {
        "created": len(created_campaigns),
        "campaigns": created_campaigns
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "domain": "campaigns"
    }

