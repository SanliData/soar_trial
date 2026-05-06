***REMOVED*** -*- coding: utf-8 -*-
"""
Mobile Geo Targeting Service - Mobile device location-based targeting
Handles GPS coordinate targeting for mobile devices
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.b2b_campaign import Campaign, CampaignStatus
from backend.db import SessionLocal
from backend.services.b2b.geo_targeting_service import geo_targeting_service
import math


class MobileGeoTargetingService:
    """Mobile device location-based targeting service"""
    
    def __init__(self):
        self.geo_targeting = geo_targeting_service
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def check_mobile_location_for_campaign(
        self,
        campaign_id: int,
        mobile_latitude: float,
        mobile_longitude: float,
        device_type: str = "mobile"  ***REMOVED*** mobile, tablet, desktop
    ) -> Dict:
        """
        Check if mobile device location matches campaign targeting
        Returns whether ad should be shown and targeting details
        """
        db = self._get_db()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return {"should_show": False, "reason": "Campaign not found"}
            
            ***REMOVED*** Check if campaign is active
            if campaign.status != CampaignStatus.ACTIVE.value:
                return {"should_show": False, "reason": "Campaign not active"}
            
            ***REMOVED*** Check device type targeting
            target_device_types = campaign.target_device_types or []
            if target_device_types and device_type not in target_device_types:
                if campaign.mobile_only and device_type != "mobile":
                    return {"should_show": False, "reason": "Mobile-only campaign"}
                if target_device_types and device_type not in target_device_types:
                    return {"should_show": False, "reason": f"Device type {device_type} not targeted"}
            
            ***REMOVED*** Check GPS targeting
            if campaign.use_gps_targeting:
                ***REMOVED*** Check if within radius
                distance = self.geo_targeting.calculate_distance(
                    campaign.target_latitude,
                    campaign.target_longitude,
                    mobile_latitude,
                    mobile_longitude
                )
                
                if distance > campaign.radius_meters:
                    return {
                        "should_show": False,
                        "reason": "Outside target radius",
                        "distance_meters": distance,
                        "target_radius_meters": campaign.radius_meters
                    }
            
            ***REMOVED*** Check geofencing
            if campaign.geofencing_enabled and campaign.geofence_polygon:
                is_inside = self._check_point_in_polygon(
                    mobile_latitude,
                    mobile_longitude,
                    campaign.geofence_polygon
                )
                if not is_inside:
                    return {"should_show": False, "reason": "Outside geofence area"}
            
            ***REMOVED*** Calculate distance for response
            distance = self.geo_targeting.calculate_distance(
                campaign.target_latitude,
                campaign.target_longitude,
                mobile_latitude,
                mobile_longitude
            )
            
            return {
                "should_show": True,
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "distance_meters": distance,
                "target_radius_meters": campaign.radius_meters,
                "ad_content": {
                    "title": campaign.ad_title,
                    "description": campaign.ad_description,
                    "image_url": campaign.ad_image_url,
                    "landing_url": campaign.ad_landing_url,
                },
                "location_accuracy": campaign.location_accuracy
            }
        finally:
            db.close()
    
    def get_campaigns_for_mobile_location(
        self,
        mobile_latitude: float,
        mobile_longitude: float,
        device_type: str = "mobile",
        radius_meters: Optional[float] = None
    ) -> List[Dict]:
        """
        Get all active campaigns that should be shown for mobile device at given location
        """
        db = self._get_db()
        try:
            ***REMOVED*** Get all active campaigns
            active_campaigns = db.query(Campaign).filter(
                Campaign.status == CampaignStatus.ACTIVE.value
            ).all()
            
            matching_campaigns = []
            
            for campaign in active_campaigns:
                ***REMOVED*** Check device type
                target_device_types = campaign.target_device_types or []
                if target_device_types and device_type not in target_device_types:
                    if campaign.mobile_only and device_type != "mobile":
                        continue
                    if target_device_types and device_type not in target_device_types:
                        continue
                
                ***REMOVED*** Check GPS targeting
                if campaign.use_gps_targeting:
                    distance = self.geo_targeting.calculate_distance(
                        campaign.target_latitude,
                        campaign.target_longitude,
                        mobile_latitude,
                        mobile_longitude
                    )
                    
                    ***REMOVED*** Use campaign radius or provided radius
                    check_radius = radius_meters if radius_meters else campaign.radius_meters
                    
                    if distance > check_radius:
                        continue
                
                ***REMOVED*** Check geofencing
                if campaign.geofencing_enabled and campaign.geofence_polygon:
                    is_inside = self._check_point_in_polygon(
                        mobile_latitude,
                        mobile_longitude,
                        campaign.geofence_polygon
                    )
                    if not is_inside:
                        continue
                
                ***REMOVED*** Calculate distance
                distance = self.geo_targeting.calculate_distance(
                    campaign.target_latitude,
                    campaign.target_longitude,
                    mobile_latitude,
                    mobile_longitude
                )
                
                matching_campaigns.append({
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "distance_meters": distance,
                    "ad_content": {
                        "title": campaign.ad_title,
                        "description": campaign.ad_description,
                        "image_url": campaign.ad_image_url,
                        "landing_url": campaign.ad_landing_url,
                    }
                })
            
            ***REMOVED*** Sort by distance (closest first)
            matching_campaigns.sort(key=lambda x: x["distance_meters"])
            
            return matching_campaigns
        finally:
            db.close()
    
    def _check_point_in_polygon(
        self,
        latitude: float,
        longitude: float,
        polygon: List[Dict]
    ) -> bool:
        """
        Check if point is inside polygon using ray casting algorithm
        polygon: [{"lat": float, "lng": float}, ...]
        """
        if not polygon or len(polygon) < 3:
            return True  ***REMOVED*** No geofence defined, allow all
        
        inside = False
        j = len(polygon) - 1
        
        for i in range(len(polygon)):
            xi = polygon[i].get("lat") or polygon[i].get("latitude")
            yi = polygon[i].get("lng") or polygon[i].get("longitude")
            xj = polygon[j].get("lat") or polygon[j].get("latitude")
            yj = polygon[j].get("lng") or polygon[j].get("longitude")
            
            if ((yi > longitude) != (yj > longitude)) and \
               (latitude < (xj - xi) * (longitude - yi) / (yj - yi) + xi):
                inside = not inside
            
            j = i
        
        return inside
    
    def create_mobile_geo_campaign(
        self,
        company_id: int,
        target_persona_id: int,
        name: str,
        ad_title: str,
        ad_description: str,
        ad_landing_url: str,
        target_latitude: float,
        target_longitude: float,
        radius_meters: float = 10.0,
        mobile_only: bool = True,
        geofence_polygon: Optional[List[Dict]] = None,
        real_time_tracking: bool = False
    ) -> Campaign:
        """Create mobile-specific geo-targeted campaign"""
        ***REMOVED*** Use base geo-targeting service
        campaign = self.geo_targeting.create_geo_targeted_campaign(
            company_id=company_id,
            target_persona_id=target_persona_id,
            name=name,
            ad_title=ad_title,
            ad_description=ad_description,
            ad_landing_url=ad_landing_url,
            radius_meters=radius_meters,
            ad_platform="google_ads_mobile"  ***REMOVED*** Mobile-specific platform
        )
        
        ***REMOVED*** Update mobile-specific fields
        db = self._get_db()
        try:
            campaign.target_device_types = ["mobile", "tablet"]
            campaign.mobile_only = mobile_only
            campaign.use_gps_targeting = True
            campaign.geofencing_enabled = geofence_polygon is not None
            campaign.geofence_polygon = geofence_polygon or []
            campaign.real_time_location_tracking = real_time_tracking
            
            db.commit()
            db.refresh(campaign)
            
            return campaign
        finally:
            db.close()
    
    def track_mobile_location(
        self,
        campaign_id: int,
        mobile_latitude: float,
        mobile_longitude: float,
        device_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict:
        """
        Track mobile device location for real-time targeting
        Updates campaign performance if ad is shown
        """
        db = self._get_db()
        try:
            campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                return {"success": False, "error": "Campaign not found"}
            
            ***REMOVED*** Check if should show ad
            result = self.check_mobile_location_for_campaign(
                campaign_id=campaign_id,
                mobile_latitude=mobile_latitude,
                mobile_longitude=mobile_longitude,
                device_type="mobile"
            )
            
            if result.get("should_show"):
                ***REMOVED*** Track impression
                campaign.impressions += 1
                campaign.updated_at = datetime.utcnow()
                db.commit()
                
                ***REMOVED*** Store location tracking data in metadata
                tracking_data = campaign.metadata.get("mobile_location_tracking", [])
                tracking_data.append({
                    "device_id": device_id,
                    "latitude": mobile_latitude,
                    "longitude": mobile_longitude,
                    "timestamp": (timestamp or datetime.utcnow()).isoformat(),
                    "distance_meters": result.get("distance_meters")
                })
                campaign.metadata["mobile_location_tracking"] = tracking_data
                db.commit()
            
            return {
                "success": True,
                "should_show": result.get("should_show"),
                "campaign_id": campaign_id,
                "distance_meters": result.get("distance_meters")
            }
        finally:
            db.close()


***REMOVED*** Global instance
mobile_geo_targeting_service = MobileGeoTargetingService()

