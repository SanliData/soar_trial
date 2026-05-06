"""
MODEL: enrichment_settings
PURPOSE: Enrichment settings model for compliance-first email/contact enrichment
ENCODING: UTF-8 WITHOUT BOM

Controls email and contact enrichment with confidence thresholds and explicit consent.
"""

from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class EnrichmentSettings(Base):
    """
    Enrichment settings model for compliance-first enrichment.
    Each user has enrichment settings with confidence thresholds and consent tracking.
    """
    
    __tablename__ = "enrichment_settings"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User (one-to-one relationship)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    ***REMOVED*** Confidence thresholds (0.0 to 1.0)
    email_confidence_threshold = Column(Float, default=0.8, nullable=False)  ***REMOVED*** Minimum confidence for email enrichment
    phone_confidence_threshold = Column(Float, default=0.8, nullable=False)  ***REMOVED*** Minimum confidence for phone enrichment
    
    ***REMOVED*** Consent tracking
    require_explicit_consent = Column(Boolean, default=True, nullable=False)  ***REMOVED*** Require explicit consent before enrichment
    consent_given = Column(Boolean, default=False, nullable=False)  ***REMOVED*** Has user given explicit consent?
    consent_given_at = Column(DateTime(timezone=True), nullable=True)  ***REMOVED*** When consent was given
    
    ***REMOVED*** Opt-in preferences
    enable_email_enrichment = Column(Boolean, default=False, nullable=False)  ***REMOVED*** Opt-in for email enrichment
    enable_phone_enrichment = Column(Boolean, default=False, nullable=False)  ***REMOVED*** Opt-in for phone enrichment
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship
    user = relationship("User", backref="enrichment_settings", uselist=False)
    
    def __repr__(self):
        return f"<EnrichmentSettings(user_id={self.user_id}, email_threshold={self.email_confidence_threshold}, consent_given={self.consent_given})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email_confidence_threshold": self.email_confidence_threshold,
            "phone_confidence_threshold": self.phone_confidence_threshold,
            "require_explicit_consent": self.require_explicit_consent,
            "consent_given": self.consent_given,
            "consent_given_at": self.consent_given_at.isoformat() if self.consent_given_at else None,
            "enable_email_enrichment": self.enable_email_enrichment,
            "enable_phone_enrichment": self.enable_phone_enrichment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
