"""
MODEL: usage_tracking
PURPOSE: Usage tracking model for plan limits
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index, Float
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class UsageTracking(Base):
    """
    Usage tracking model for monitoring user's monthly usage against plan limits.
    Tracks companies, personas, campaigns, etc.
    """
    
    __tablename__ = "usage_tracking"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Usage period (YYYY-MM format)
    period = Column(String(7), nullable=False, index=True)   # e.g., "2024-01"
    
    # Usage counters
    companies_count = Column(Integer, default=0, nullable=False)
    personas_count = Column(Integer, default=0, nullable=False)
    campaigns_count = Column(Integer, default=0, nullable=False)
    appointments_count = Column(Integer, default=0, nullable=False)
    leads_count = Column(Integer, default=0, nullable=False)
    
    # Usage-based billing counters
    verified_company_count = Column(Integer, default=0, nullable=False)
    decision_maker_match_count = Column(Integer, default=0, nullable=False)
    persona_enrichment_count = Column(Integer, default=0, nullable=False)
    location_exposure_count = Column(Integer, default=0, nullable=False)
    outreach_attempt_count = Column(Integer, default=0, nullable=False)
    booked_meeting_count = Column(Integer, default=0, nullable=False)
    
    # Usage cost (cumulative for period)
    usage_cost = Column(Float, default=0.0, nullable=False)   # Total usage cost for period
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to User
    user = relationship("User", backref="usage_tracking")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_usage_user_period', 'user_id', 'period', unique=True),
        Index('idx_usage_period', 'period'),
    )
    
    def __repr__(self):
        return f"<UsageTracking(id={self.id}, user_id={self.user_id}, period='{self.period}', companies={self.companies_count}, personas={self.personas_count})>"
    
    def to_dict(self):
        """
        Convert usage tracking to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "period": self.period,
            "companies_count": self.companies_count,
            "personas_count": self.personas_count,
            "campaigns_count": self.campaigns_count,
            "appointments_count": self.appointments_count,
            "leads_count": self.leads_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


