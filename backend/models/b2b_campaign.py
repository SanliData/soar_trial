***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Campaign Model - Location-based advertising campaigns
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.db import Base


class CampaignStatus(str, enum.Enum):
    """Campaign statuses"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Location-based advertising campaign (10 meter accuracy)"""
    __tablename__ = "b2b_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("b2b_products.id"), nullable=True, index=True)  ***REMOVED*** Related product
    company_id = Column(Integer, ForeignKey("b2b_companies.id"), nullable=False, index=True)
    target_persona_id = Column(Integer, ForeignKey("b2b_personas.id"), nullable=False, index=True)
    
    ***REMOVED*** Campaign information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=CampaignStatus.DRAFT.value, index=True)
    
    ***REMOVED*** Location information (10 meter accuracy)
    target_latitude = Column(Float, nullable=False)
    target_longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, default=10.0)  ***REMOVED*** 10 meter radius
    location_accuracy = Column(Float)  ***REMOVED*** Accuracy in meters
    
    ***REMOVED*** Mobile targeting
    target_device_types = Column(JSON, default=list)  ***REMOVED*** ["mobile", "tablet", "desktop"]
    mobile_only = Column(Boolean, default=False)  ***REMOVED*** Mobile-only targeting
    use_gps_targeting = Column(Boolean, default=True)  ***REMOVED*** Use GPS coordinates for mobile
    geofencing_enabled = Column(Boolean, default=True)  ***REMOVED*** Enable geofencing
    geofence_polygon = Column(JSON, default=list)  ***REMOVED*** Geofence polygon coordinates
    real_time_location_tracking = Column(Boolean, default=False)  ***REMOVED*** Real-time location updates
    
    ***REMOVED*** Ad content
    ad_title = Column(String(255))
    ad_description = Column(Text)
    ad_image_url = Column(String(500))
    ad_landing_url = Column(String(500))
    ad_creative_data = Column(JSON, default=dict)  ***REMOVED*** Ad creative content
    
    ***REMOVED*** Platform information
    ad_platform = Column(String(50))  ***REMOVED*** google_ads, facebook_ads, linkedin_ads, etc.
    ad_platform_campaign_id = Column(String(100))  ***REMOVED*** Campaign ID on platform
    ad_platform_ad_id = Column(String(100))  ***REMOVED*** Ad ID on platform
    
    ***REMOVED*** Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    ***REMOVED*** Scheduling
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ***REMOVED*** Metadata
    metadata = Column(JSON, default=dict)
    
    ***REMOVED*** Relationships
    product = relationship("Product", back_populates="campaigns")
    company = relationship("Company", back_populates="campaigns")
    target_persona = relationship("Persona", back_populates="campaigns")
    appointments = relationship("Appointment", back_populates="campaign", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "company_id": self.company_id,
            "target_persona_id": self.target_persona_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "target_location": {
                "latitude": self.target_latitude,
                "longitude": self.target_longitude,
                "radius_meters": self.radius_meters,
                "location_accuracy": self.location_accuracy,
            },
            "mobile_targeting": {
                "target_device_types": self.target_device_types or [],
                "mobile_only": self.mobile_only,
                "use_gps_targeting": self.use_gps_targeting,
                "geofencing_enabled": self.geofencing_enabled,
                "geofence_polygon": self.geofence_polygon or [],
                "real_time_location_tracking": self.real_time_location_tracking,
            },
            "ad_content": {
                "title": self.ad_title,
                "description": self.ad_description,
                "image_url": self.ad_image_url,
                "landing_url": self.ad_landing_url,
                "creative_data": self.ad_creative_data or {},
            },
            "ad_platform": self.ad_platform,
            "ad_platform_campaign_id": self.ad_platform_campaign_id,
            "ad_platform_ad_id": self.ad_platform_ad_id,
            "performance": {
                "impressions": self.impressions,
                "clicks": self.clicks,
                "conversions": self.conversions,
                "cost": self.cost,
            },
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }

