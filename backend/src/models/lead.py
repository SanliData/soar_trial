"""
MODEL: lead
PURPOSE: Lead model for Google Ads Lead Form submissions
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class Lead(Base):
    """
    Lead model for storing Google Ads Lead Form submissions.
    Each lead is associated with a user and optionally a campaign.
    Leads are automatically converted to appointments (Step 11).
    """
    
    __tablename__ = "leads"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    google_ads_campaign_id = Column(String(255), nullable=True, index=True)
    
    # Contact information (from Lead Form)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    # Lead Form data (stored as JSON for flexibility)
    form_data = Column(JSON, nullable=True)   # All form fields from Google Ads
    
    # Source information
    source = Column(String(100), default="google_ads_lead_form", nullable=False)
    google_ads_lead_id = Column(String(255), nullable=True, unique=True, index=True)
    
    # Status
    status = Column(String(50), default="new", nullable=False)   # "new", "contacted", "qualified", "converted", "appointment_scheduled", "lost"
    
    # Conversion to appointment
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True, index=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="leads")
    campaign = relationship("Campaign", backref="leads")
    appointment = relationship("Appointment", backref="lead", foreign_keys=[appointment_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_lead_user_id', 'user_id'),
        Index('idx_lead_campaign_id', 'campaign_id'),
        Index('idx_lead_email', 'email'),
        Index('idx_lead_status', 'status'),
        Index('idx_lead_google_ads_lead_id', 'google_ads_lead_id'),
    )
    
    def __repr__(self):
        return f"<Lead(id={self.id}, email='{self.email}', user_id={self.user_id}, status='{self.status}')>"
    
    def to_dict(self):
        """
        Convert lead to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "campaign_id": self.campaign_id,
            "google_ads_campaign_id": self.google_ads_campaign_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "form_data": self.form_data,
            "source": self.source,
            "google_ads_lead_id": self.google_ads_lead_id,
            "status": self.status,
            "appointment_id": self.appointment_id,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


