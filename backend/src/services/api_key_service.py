"""
SERVICE: api_key_service
PURPOSE: Enterprise API key management service
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.models.api_key import APIKey

logger = logging.getLogger(__name__)


class APIKeyService:
    """Enterprise API key management service"""
    
    @staticmethod
    def hash_key(key: str) -> str:
        """
        Hash API key for storage (SHA-256).
        
        Args:
            key: Plain text API key
            
        Returns:
            SHA-256 hash of the key
        """
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def generate_key(prefix: str = "sk_live") -> str:
        """
        Generate new API key.
        
        Args:
            prefix: Key prefix (e.g., "sk_live", "sk_test")
            
        Returns:
            Generated API key (e.g., "sk_live_abc123def456...")
        """
        # Generate random suffix (32 bytes = 64 hex chars)
        random_suffix = secrets.token_hex(32)
        return f"{prefix}_{random_suffix}"
    
    @staticmethod
    def validate_key(db: Session, key: str) -> Optional[APIKey]:
        """
        Validate API key against database.
        
        Args:
            db: Database session
            key: API key to validate
            
        Returns:
            APIKey object if valid, None otherwise
        """
        # Hash the key
        key_hash = APIKeyService.hash_key(key)
        
        # Look up in database
        api_key = db.query(APIKey).filter(
            and_(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            )
        ).first()
        
        if api_key is None:
            return None
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            logger.warning(f"⚠️ API key expired: {api_key.key_prefix}***")
            return None
        
        # Update last_used_at
        api_key.last_used_at = datetime.utcnow()
        db.commit()
        
        return api_key
    
    @staticmethod
    def create_key(
        db: Session,
        company: Optional[str] = None,
        company_id: Optional[int] = None,
        tier: str = "standard",
        quota_per_minute: int = 100,
        quota_per_day: int = 10000,
        quota_per_month: int = 300000,
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create new API key.
        
        Args:
            db: Database session
            company: Company name
            company_id: Company ID
            tier: Key tier ("free", "standard", "premium", "enterprise")
            quota_per_minute: Requests per minute
            quota_per_day: Requests per day
            quota_per_month: Requests per month
            expires_in_days: Expiration in days (None = no expiration)
            
        Returns:
            Dictionary with key and metadata
        """
        # Generate key
        plain_key = APIKeyService.generate_key()
        key_hash = APIKeyService.hash_key(plain_key)
        key_prefix = plain_key[:10]   # First 10 chars for identification
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key = APIKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            company=company,
            company_id=company_id,
            tier=tier,
            quota_per_minute=quota_per_minute,
            quota_per_day=quota_per_day,
            quota_per_month=quota_per_month,
            expires_at=expires_at,
            is_active=True
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        logger.info(f"✅ API key created: {key_prefix}*** (tier: {tier}, company: {company})")
        
        # Return plain key (only shown once during creation)
        return {
            "id": api_key.id,
            "key": plain_key,   # Only shown once!
            "key_prefix": key_prefix,
            "tier": tier,
            "quota_per_minute": quota_per_minute,
            "quota_per_day": quota_per_day,
            "quota_per_month": quota_per_month,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": api_key.created_at.isoformat()
        }
    
    @staticmethod
    def revoke_key(db: Session, key_id: int) -> bool:
        """
        Revoke API key (set is_active=False).
        
        Args:
            db: Database session
            key_id: API key ID
            
        Returns:
            True if revoked, False otherwise
        """
        api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
        
        if api_key is None:
            return False
        
        api_key.is_active = False
        api_key.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"✅ API key revoked: {api_key.key_prefix}***")
        return True
    
    @staticmethod
    def get_key_by_id(db: Session, key_id: int) -> Optional[APIKey]:
        """Get API key by ID"""
        return db.query(APIKey).filter(APIKey.id == key_id).first()
    
    @staticmethod
    def list_keys(db: Session, company_id: Optional[int] = None, tier: Optional[str] = None, active_only: bool = True) -> list[APIKey]:
        """
        List API keys with filters.
        
        Args:
            db: Database session
            company_id: Filter by company ID
            tier: Filter by tier
            active_only: Only return active keys
            
        Returns:
            List of APIKey objects
        """
        query = db.query(APIKey)
        
        if company_id:
            query = query.filter(APIKey.company_id == company_id)
        
        if tier:
            query = query.filter(APIKey.tier == tier)
        
        if active_only:
            query = query.filter(APIKey.is_active == True)
        
        return query.order_by(APIKey.created_at.desc()).all()
