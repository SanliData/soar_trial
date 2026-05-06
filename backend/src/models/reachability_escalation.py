"""
MODEL: reachability_escalation
PURPOSE: Direct outreach module (optional, disabled by default) for appointment/escalation
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class ReachabilityEscalation(Base):
    """
    Reachability escalation model for direct outreach (appointments).
    Optional module - disabled by default.
    Only activated when user explicitly enables it.
    Prepares architecture for call center partnerships.
    """
    
    __tablename__ = "reachability_escalations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    precision_exposure_id = Column(Integer, ForeignKey("precision_exposures.id"), nullable=True, index=True)
    
    # Escalation details
    escalation_type = Column(String(50), default="appointment", nullable=False)   # "appointment", "callback", "referral"
    title = Column(String(255), nullable=True)   # Appointment/escalation title
    description = Column(Text, nullable=True)   # Description/notes
    
    # Contact preference (optional, only if user enables)
    contact_preference = Column(String(50), nullable=True)   # "email", "phone", "linkedin", "call_center"
    
    # Call center partnership (future)
    call_center_partner_id = Column(String(255), nullable=True)   # Partner ID if using call center
    call_center_status = Column(String(50), nullable=True)   # "pending", "assigned", "completed"
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)   # "pending", "scheduled", "completed", "cancelled"
    is_enabled = Column(Boolean, default=False, nullable=False, index=True)   # Module enabled flag
    
    # Escalation context (no personal identifiers in preview)
    escalation_context = Column(JSON, nullable=True)   # Contextual data (roles, location, etc.)
    
    # Timestamps
    scheduled_at = Column(DateTime(timezone=True), nullable=True)   # Scheduled escalation time
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="reachability_escalations")
    precision_exposure = relationship("PrecisionExposure", backref="escalations")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_escalation_user_id', 'user_id'),
        Index('idx_escalation_exposure_id', 'precision_exposure_id'),
        Index('idx_escalation_status', 'status'),
        Index('idx_escalation_enabled', 'is_enabled'),
    )
    
    def __repr__(self):
        return f"<ReachabilityEscalation(id={self.id}, escalation_type='{self.escalation_type}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert escalation to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "precision_exposure_id": self.precision_exposure_id,
            "escalation_type": self.escalation_type,
            "title": self.title,
            "description": self.description,
            "contact_preference": self.contact_preference,
            "call_center_partner_id": self.call_center_partner_id,
            "call_center_status": self.call_center_status,
            "status": self.status,
            "is_enabled": self.is_enabled,
            "escalation_context": self.escalation_context,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
