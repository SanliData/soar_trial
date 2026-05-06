***REMOVED*** -*- coding: utf-8 -*-
"""
Geo Targeting Service - Location-based advertising service
Creates ads that target individuals will see with 10 meter accuracy
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.models.b2b_campaign import Campaign, CampaignStatus
from backend.models.b2b_company import Company
from backend.models.b2b_persona import Persona
from backend.db import SessionLocal
import math
import os


class GeoTargetingService:
    """Location-based advertising creation and management service (10 meter accuracy)"""
    
    ***REMOVED*** Earth radius (meters)
    EARTH_RADIUS_METERS = 6371000
    
    def __init__(self):
        self.google_ads_api_key = os.getenv("GOOGLE_ADS_API_KEY")
        self.facebook_ads_api_key = os.getenv("FACEBOOK_ADS_API_KEY")
        self.linkedin_ads_api_key = os.getenv("LINKEDIN_ADS_API_KEY")
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate distance between two coordinates (Haversine formula)
        Result: in meters
        """
        ***REMOVED*** Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        ***REMOVED*** Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        ***REMOVED*** Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = self.EARTH_RADIUS_METERS * c
        
        return distance
    
    def is_within_radius(
        self,
        target_lat: float,
        target_lon: float,
        check_lat: float,
        check_lon: float,
        radius_meters: float = 10.0
    ) -> bool:
        """Check if within specified radius"""
        distance = self.calculate_distance(target_lat, target_lon, check_lat, check_lon)
        return distance <= radius_meters
    
    def create_geo_targeted_campaign(
        self,
        company_id: int,
        target_persona_id: int,
        name: str,
        description: Optional[str] = None,
        ad_title: str,
        ad_description: str,
        ad_image_url: Optional[str] = None,
        ad_landing_url: str,
        radius_meters: float = 10.0,
        ad_platform: str = "google_ads",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        target_device_types: Optional[List[str]] = None,
        mobile_only: bool = False,
        geofence_polygon: Optional[List[Dict]] = None,
        real_time_tracking: bool = False
    ) -> Campaign:
        """Create location-based advertising campaign"""
        db = self._get_db()
        try:
            ***REMOVED*** Get company and persona information
            company = db.query(Company).filter(Company.id == company_id).first()
            persona = db.query(Persona).filter(Persona.id == target_persona_id).first()
            
            if not company or not persona:
                raise ValueError("Company or Persona not found")
            
            ***REMOVED*** Use company coordinates (10 meter accuracy)
            if not company.latitude or not company.longitude:
                raise ValueError("Company location coordinates not available")
            
            ***REMOVED*** Create campaign
            campaign = Campaign(
                company_id=company_id,
                target_persona_id=target_persona_id,
                name=name,
                description=description,
                status=CampaignStatus.DRAFT.value,
                target_latitude=company.latitude,
                target_longitude=company.longitude,
                radius_meters=radius_meters,
                location_accuracy=10.0,  ***REMOVED*** 10 meter accuracy
                ad_title=ad_title,
                ad_description=ad_description,
                ad_image_url=ad_image_url,
                ad_landing_url=ad_landing_url,
                ad_platform=ad_platform,
                ***REMOVED*** Mobile targeting
                target_device_types=target_device_types or [],
                mobile_only=mobile_only,
                use_gps_targeting=True,
                geofencing_enabled=geofence_polygon is not None,
                geofence_polygon=geofence_polygon or [],
                real_time_location_tracking=real_time_tracking,
                start_date=start_date or datetime.utcnow(),
                end_date=end_date,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            
            return campaign
        finally:
            db.close()
    
    def create_campaign_for_persona_location(
        self,
        persona_id: int,
        campaign_name: str,
        ad_title: str,
        ad_description: str,
        ad_landing_url: str,
        radius_meters: float = 10.0
    ) -> Optional[Campaign]:
        """
        Create campaign based on persona's location
        Uses the location of persona's company
        """
        db = self._get_db()
        try:
            persona = db.query(Persona).filter(Persona.id == persona_id).first()
            
            if not persona:
                return None
            
            company = db.query(Company).filter(Company.id == persona.company_id).first()
            
            if not company or not company.latitude or not company.longitude:
                return None
            
            return self.create_geo_targeted_campaign(
                company_id=persona.company_id,
                target_persona_id=persona_id,
                name=campaign_name,
                ad_title=ad_title,
                ad_description=ad_description,
                ad_landing_url=ad_landing_url,
                radius_meters=radius_meters
            )
        finally:
            db.close()
    
    def publish_campaign_to_platform(self, campaign_id: int) -> Dict:
        """
        Publish campaign to advertising platform
        Google Ads, Facebook Ads, LinkedIn Ads, etc.
        """
        db = self._get_db()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            
            if not campaign:
                return {"success": False, "error": "Campaign not found"}
            
            platform = campaign.ad_platform
            
            if platform == "google_ads":
                return self._publish_to_google_ads(campaign, db)
            elif platform == "facebook_ads":
                return self._publish_to_facebook_ads(campaign, db)
            elif platform == "linkedin_ads":
                return self._publish_to_linkedin_ads(campaign, db)
            else:
                return {"success": False, "error": f"Unsupported platform: {platform}"}
        finally:
            db.close()
    
    def _publish_to_google_ads(self, campaign: Campaign, db: Session) -> Dict:
        """Publish campaign to Google Ads"""
        ***REMOVED*** Google Ads API integration
        ***REMOVED*** Real implementation should use Google Ads API
        
        ***REMOVED*** Sample structure
        try:
            ***REMOVED*** Google Ads API call will be made
            ***REMOVED*** campaign_id = google_ads_api.create_campaign(...)
            
            ***REMOVED*** Update campaign status
            campaign.status = CampaignStatus.ACTIVE.value
            campaign.ad_platform_campaign_id = "google_ads_campaign_123"  ***REMOVED*** Real ID
            campaign.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "platform": "google_ads",
                "campaign_id": campaign.ad_platform_campaign_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _publish_to_facebook_ads(self, campaign: Campaign, db: Session) -> Dict:
        """Publish campaign to Facebook Ads"""
        ***REMOVED*** Facebook Ads API integration
        ***REMOVED*** Real implementation should use Facebook Marketing API
        
        try:
            ***REMOVED*** Facebook Ads API call will be made
            
            campaign.status = CampaignStatus.ACTIVE.value
            campaign.ad_platform_campaign_id = "facebook_ads_campaign_123"
            campaign.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "platform": "facebook_ads",
                "campaign_id": campaign.ad_platform_campaign_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _publish_to_linkedin_ads(self, campaign: Campaign, db: Session) -> Dict:
        """Publish campaign to LinkedIn Ads"""
        ***REMOVED*** LinkedIn Ads API integration
        ***REMOVED*** Real implementation should use LinkedIn Marketing API
        
        try:
            ***REMOVED*** LinkedIn Ads API call will be made
            
            campaign.status = CampaignStatus.ACTIVE.value
            campaign.ad_platform_campaign_id = "linkedin_ads_campaign_123"
            campaign.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "platform": "linkedin_ads",
                "campaign_id": campaign.ad_platform_campaign_id
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_campaign_performance(
        self,
        campaign_id: int,
        impressions: Optional[int] = None,
        clicks: Optional[int] = None,
        conversions: Optional[int] = None,
        cost: Optional[float] = None
    ) -> Optional[Campaign]:
        """Update campaign performance metrics"""
        db = self._get_db()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            
            if not campaign:
                return None
            
            if impressions is not None:
                campaign.impressions = impressions
            if clicks is not None:
                campaign.clicks = clicks
            if conversions is not None:
                campaign.conversions = conversions
            if cost is not None:
                campaign.cost = cost
            
            campaign.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(campaign)
            
            return campaign
        finally:
            db.close()
    
    def get_campaigns_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 10.0
    ) -> List[Campaign]:
        """Get active campaigns at specific location"""
        db = self._get_db()
        try:
            all_campaigns = db.query(Campaign).filter(
                Campaign.status == CampaignStatus.ACTIVE.value
            ).all()
            
            nearby_campaigns = []
            for campaign in all_campaigns:
                if self.is_within_radius(
                    campaign.target_latitude,
                    campaign.target_longitude,
                    latitude,
                    longitude,
                    radius_meters
                ):
                    nearby_campaigns.append(campaign)
            
            return nearby_campaigns
        finally:
            db.close()
    
    def get_campaign_statistics(self, campaign_id: Optional[int] = None) -> Dict:
        """Get campaign statistics"""
        db = self._get_db()
        try:
            if campaign_id:
                campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
                if not campaign:
                    return {}
                
                return {
                    "campaign_id": campaign.id,
                    "name": campaign.name,
                    "status": campaign.status,
                    "impressions": campaign.impressions,
                    "clicks": campaign.clicks,
                    "conversions": campaign.conversions,
                    "cost": campaign.cost,
                    "ctr": (campaign.clicks / campaign.impressions * 100) if campaign.impressions > 0 else 0,
                    "conversion_rate": (campaign.conversions / campaign.clicks * 100) if campaign.clicks > 0 else 0,
                    "cpc": (campaign.cost / campaign.clicks) if campaign.clicks > 0 else 0,
                }
            else:
                all_campaigns = db.query(Campaign).all()
                
                return {
                    "total_campaigns": len(all_campaigns),
                    "active": len([c for c in all_campaigns if c.status == CampaignStatus.ACTIVE.value]),
                    "total_impressions": sum(c.impressions for c in all_campaigns),
                    "total_clicks": sum(c.clicks for c in all_campaigns),
                    "total_conversions": sum(c.conversions for c in all_campaigns),
                    "total_cost": sum(c.cost for c in all_campaigns),
                }
        finally:
            db.close()


***REMOVED*** Global instance
geo_targeting_service = GeoTargetingService()

