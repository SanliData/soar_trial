"""
MODEL: appointment
PURPOSE: Appointment model for scheduled meetings
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class Appointment(Base):
    """
    Appointment model for storing scheduled meetings.
    Each appointment is associated with a user and optionally a persona/company.
    """
    
    __tablename__ = "appointments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    
    # Appointment information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30, nullable=False)
    
    # Location
    location = Column(String(512), nullable=True)   # Physical location or "virtual"
    meeting_url = Column(String(512), nullable=True)   # For virtual meetings
    
    # Contact information
    contact_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Status
    status = Column(String(50), default="scheduled", nullable=False)   # "scheduled", "confirmed", "completed", "cancelled", "no_show"
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="appointments")
    persona = relationship("Persona", backref="appointments")
    company = relationship("Company", backref="appointments")
    campaign = relationship("Campaign", backref="appointments")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_appointment_user_id', 'user_id'),
        Index('idx_appointment_persona_id', 'persona_id'),
        Index('idx_appointment_company_id', 'company_id'),
        Index('idx_appointment_scheduled_at', 'scheduled_at'),
        Index('idx_appointment_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, title='{self.title}', user_id={self.user_id}, scheduled_at='{self.scheduled_at}')>"
    
    def to_dict(self):
        """
        Convert appointment to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "company_id": self.company_id,
            "campaign_id": self.campaign_id,
            "title": self.title,
            "description": self.description,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "meeting_url": self.meeting_url,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


