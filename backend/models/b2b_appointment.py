***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Appointment Model - Appointment management
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.db import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment statuses"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RESCHEDULED = "rescheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base):
    """Appointment with target individual"""
    __tablename__ = "b2b_appointments"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("b2b_campaigns.id"), nullable=False, index=True)
    persona_id = Column(Integer, ForeignKey("b2b_personas.id"), nullable=False, index=True)
    
    ***REMOVED*** Appointment information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=AppointmentStatus.PENDING.value, index=True)
    
    ***REMOVED*** Scheduling
    scheduled_at = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, default=30)
    timezone = Column(String(50), default="UTC")
    
    ***REMOVED*** Contact information
    contact_method = Column(String(50))  ***REMOVED*** email, phone, linkedin, in_person, video_call
    contact_details = Column(JSON, default=dict)  ***REMOVED*** Email address, phone, video link, etc.
    
    ***REMOVED*** Location (if in-person)
    location_type = Column(String(50))  ***REMOVED*** in_person, virtual, phone
    location_address = Column(String(500))
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    meeting_link = Column(String(500))  ***REMOVED*** Zoom, Teams, Google Meet link
    
    ***REMOVED*** Follow-up information
    reminder_sent = Column(Boolean, default=False)
    reminder_sent_at = Column(DateTime)
    follow_up_required = Column(Boolean, default=False)
    follow_up_notes = Column(Text)
    
    ***REMOVED*** Outcome
    outcome = Column(String(50))  ***REMOVED*** interested, not_interested, follow_up, qualified, etc.
    outcome_notes = Column(Text)
    next_steps = Column(Text)
    
    ***REMOVED*** Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)
    
    ***REMOVED*** Relationships
    campaign = relationship("Campaign", back_populates="appointments")
    persona = relationship("Persona", back_populates="appointments")

    def to_dict(self):
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "persona_id": self.persona_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "duration_minutes": self.duration_minutes,
            "timezone": self.timezone,
            "contact_method": self.contact_method,
            "contact_details": self.contact_details or {},
            "location": {
                "type": self.location_type,
                "address": self.location_address,
                "latitude": self.location_latitude,
                "longitude": self.location_longitude,
                "meeting_link": self.meeting_link,
            },
            "reminder_sent": self.reminder_sent,
            "reminder_sent_at": self.reminder_sent_at.isoformat() if self.reminder_sent_at else None,
            "follow_up_required": self.follow_up_required,
            "follow_up_notes": self.follow_up_notes,
            "outcome": self.outcome,
            "outcome_notes": self.outcome_notes,
            "next_steps": self.next_steps,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }

