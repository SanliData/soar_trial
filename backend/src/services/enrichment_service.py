"""
SERVICE: enrichment_service
PURPOSE: Compliance-first enrichment service with confidence thresholds and consent
ENCODING: UTF-8 WITHOUT BOM

Email and contact enrichment with:
- Confidence thresholds
- Explicit user consent
- Opt-in preferences
"""

from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from src.models.enrichment_settings import EnrichmentSettings
from src.models.user import User


class EnrichmentService:
    """Service for compliance-first enrichment"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_settings(self, user_id: int) -> EnrichmentSettings:
        """Get or create enrichment settings for a user"""
        settings = self.db.query(EnrichmentSettings).filter(
            EnrichmentSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = EnrichmentSettings(
                user_id=user_id,
                email_confidence_threshold=0.8,
                phone_confidence_threshold=0.8,
                require_explicit_consent=True,
                consent_given=False,
                enable_email_enrichment=False,
                enable_phone_enrichment=False
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_settings(
        self,
        user_id: int,
        email_confidence_threshold: Optional[float] = None,
        phone_confidence_threshold: Optional[float] = None,
        require_explicit_consent: Optional[bool] = None,
        enable_email_enrichment: Optional[bool] = None,
        enable_phone_enrichment: Optional[bool] = None
    ) -> EnrichmentSettings:
        """Update enrichment settings"""
        settings = self.get_or_create_settings(user_id)
        
        if email_confidence_threshold is not None:
            if not (0.0 <= email_confidence_threshold <= 1.0):
                raise ValueError("email_confidence_threshold must be between 0.0 and 1.0")
            settings.email_confidence_threshold = email_confidence_threshold
        
        if phone_confidence_threshold is not None:
            if not (0.0 <= phone_confidence_threshold <= 1.0):
                raise ValueError("phone_confidence_threshold must be between 0.0 and 1.0")
            settings.phone_confidence_threshold = phone_confidence_threshold
        
        if require_explicit_consent is not None:
            settings.require_explicit_consent = require_explicit_consent
        
        if enable_email_enrichment is not None:
            settings.enable_email_enrichment = enable_email_enrichment
        
        if enable_phone_enrichment is not None:
            settings.enable_phone_enrichment = enable_phone_enrichment
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def give_consent(self, user_id: int) -> EnrichmentSettings:
        """Record explicit user consent for enrichment"""
        settings = self.get_or_create_settings(user_id)
        
        settings.consent_given = True
        settings.consent_given_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def revoke_consent(self, user_id: int) -> EnrichmentSettings:
        """Revoke user consent for enrichment"""
        settings = self.get_or_create_settings(user_id)
        
        settings.consent_given = False
        settings.consent_given_at = None
        settings.enable_email_enrichment = False
        settings.enable_phone_enrichment = False
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
    
    def can_enrich_email(
        self,
        user_id: int,
        confidence: float
    ) -> Tuple[bool, str]:
        """
        Check if email enrichment is allowed for a user with given confidence.
        
        Returns:
            (allowed: bool, reason: str)
        """
        settings = self.get_or_create_settings(user_id)
        
        # Check consent
        if settings.require_explicit_consent and not settings.consent_given:
            return False, "Explicit consent required but not given"
        
        # Check opt-in
        if not settings.enable_email_enrichment:
            return False, "Email enrichment not enabled by user"
        
        # Check confidence threshold
        if confidence < settings.email_confidence_threshold:
            return False, f"Confidence {confidence} below threshold {settings.email_confidence_threshold}"
        
        return True, "Enrichment allowed"
    
    def can_enrich_phone(
        self,
        user_id: int,
        confidence: float
    ) -> Tuple[bool, str]:
        """
        Check if phone enrichment is allowed for a user with given confidence.
        
        Returns:
            (allowed: bool, reason: str)
        """
        settings = self.get_or_create_settings(user_id)
        
        # Check consent
        if settings.require_explicit_consent and not settings.consent_given:
            return False, "Explicit consent required but not given"
        
        # Check opt-in
        if not settings.enable_phone_enrichment:
            return False, "Phone enrichment not enabled by user"
        
        # Check confidence threshold
        if confidence < settings.phone_confidence_threshold:
            return False, f"Confidence {confidence} below threshold {settings.phone_confidence_threshold}"
        
        return True, "Enrichment allowed"
