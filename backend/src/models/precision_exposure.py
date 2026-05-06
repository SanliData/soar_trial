"""
MODEL: precision_exposure
PURPOSE: Precision exposure campaign model (contextual targeting, no personal identifiers)
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class PrecisionExposure(Base):
    """
    Precision exposure campaign model.
    Targets by location + persona context, NOT by individual identifiers.
    No personal data until explicit outreach stage.
    """
    
    __tablename__ = "precision_exposures"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feasibility_report_id = Column(Integer, ForeignKey("feasibility_reports.id"), nullable=True, index=True)
    
    # Campaign context (NOT personal identifiers)
    campaign_name = Column(String(255), nullable=False)
    target_geography = Column(Text, nullable=True)   # Geographic region
    target_roles = Column(String(500), nullable=True)   # "CEO, CTO" (roles, not names)
    target_industry = Column(String(255), nullable=True)   # Industry context
    
    # Location targeting (contextual)
    location_coordinates = Column(JSON, nullable=True)   # {"lat": 41.0082, "lng": 28.9784}
    location_radius_meters = Column(Integer, nullable=True)   # Radius in meters
    location_polygon = Column(JSON, nullable=True)   # GeoJSON polygon for custom areas
    
    # Exposure management type
    management_type = Column(String(50), default="soar_managed", nullable=False)   # "soar_managed", "partner_managed", "customer_agency"
    
    # Status
    status = Column(String(50), default="draft", nullable=False, index=True)   # "draft", "active", "paused", "completed"
    
    # Targeting context (anonymized)
    target_context = Column(JSON, nullable=True)   # Contextual targeting parameters (no PII)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="precision_exposures")
    feasibility_report = relationship("FeasibilityReport", backref="precision_exposures")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_exposure_user_id', 'user_id'),
        Index('idx_exposure_report_id', 'feasibility_report_id'),
        Index('idx_exposure_status', 'status'),
    )
    
    def __repr__(self):
        return f"<PrecisionExposure(id={self.id}, campaign_name='{self.campaign_name}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert exposure campaign to dictionary (no personal identifiers)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feasibility_report_id": self.feasibility_report_id,
            "campaign_name": self.campaign_name,
            "target_geography": self.target_geography,
            "target_roles": self.target_roles,
            "target_industry": self.target_industry,
            "location_coordinates": self.location_coordinates,
            "location_radius_meters": self.location_radius_meters,
            "location_polygon": self.location_polygon,
            "management_type": self.management_type,
            "status": self.status,
            "target_context": self.target_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None
        }
