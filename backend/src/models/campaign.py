"""
MODEL: campaign
PURPOSE: Campaign model for advertising campaigns
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Campaign(Base):
    """
    Campaign model for storing advertising campaigns.
    Each campaign is associated with a user.
    """
    
    __tablename__ = "campaigns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Campaign information
    name = Column(String(255), nullable=False)
    ad_content_type = Column(String(50), nullable=False)   # "text", "image", "link"
    ad_content = Column(Text, nullable=False)   # Text, image URL, or link URL
    ad_type = Column(String(50), nullable=False)   # "location-based", "social", "email", "sms"
    
    # Target information (stored as JSON)
    target_data = Column(JSON, nullable=True)   # Company IDs, personnel IDs, locations, etc.
    
    # Scheduling and budget
    schedule = Column(JSON, nullable=True)   # Scheduling options
    budget = Column(Float, nullable=True)
    max_impressions = Column(Integer, nullable=True)
    
    # Statistics
    total_targets = Column(Integer, default=0, nullable=False)
    companies_count = Column(Integer, default=0, nullable=False)
    personnel_count = Column(Integer, default=0, nullable=False)
    locations_count = Column(Integer, default=0, nullable=False)
    
    # Campaign metrics
    impressions = Column(Integer, default=0, nullable=False)
    clicks = Column(Integer, default=0, nullable=False)
    conversions = Column(Integer, default=0, nullable=False)
    
    # Conversion strategy
    conversion_strategy = Column(String(50), default="appointment", nullable=False)   # "appointment", "direct_traffic"
    sales_site_url = Column(String(512), nullable=True)   # URL for direct traffic campaigns
    utm_parameters = Column(JSON, nullable=True)   # UTM tracking parameters
    
    # Status
    status = Column(String(50), default="draft", nullable=False)   # "draft", "active", "paused", "completed", "stopped"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship to User
    user = relationship("User", backref="campaigns")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_campaign_user_id', 'user_id'),
        Index('idx_campaign_status', 'status'),
        Index('idx_campaign_name', 'name'),
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name='{self.name}', user_id={self.user_id}, status='{self.status}')>"
    
    def to_dict(self):
        """
        Convert campaign to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "ad_content_type": self.ad_content_type,
            "ad_content": self.ad_content,
            "ad_type": self.ad_type,
            "target_data": self.target_data,
            "schedule": self.schedule,
            "budget": self.budget,
            "max_impressions": self.max_impressions,
            "total_targets": self.total_targets,
            "companies_count": self.companies_count,
            "personnel_count": self.personnel_count,
            "locations_count": self.locations_count,
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "conversion_strategy": self.conversion_strategy,
            "sales_site_url": self.sales_site_url,
            "utm_parameters": self.utm_parameters,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

