"""
MODEL: api_key
PURPOSE: Enterprise API key management with database storage
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class APIKey(Base):
    """
    Enterprise API key model.
    Supports tier-based rate limiting, quotas, and expiration.
    """
    
    __tablename__ = "api_keys"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** API key (hashed for storage)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)
    
    ***REMOVED*** Key metadata (for display)
    key_prefix = Column(String(10), nullable=False)  ***REMOVED*** First 5 chars for identification
    
    ***REMOVED*** Company/Organization
    company = Column(String(255), nullable=True, index=True)
    company_id = Column(Integer, nullable=True, index=True)
    
    ***REMOVED*** Tier-based rate limiting
    tier = Column(String(50), default="standard", nullable=False, index=True)  ***REMOVED*** "free", "standard", "premium", "enterprise"
    
    ***REMOVED*** Quota settings
    quota_per_minute = Column(Integer, default=100, nullable=False)  ***REMOVED*** Requests per minute
    quota_per_day = Column(Integer, default=10000, nullable=False)  ***REMOVED*** Requests per day
    quota_per_month = Column(Integer, default=300000, nullable=False)  ***REMOVED*** Requests per month
    
    ***REMOVED*** Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    ***REMOVED*** Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    ***REMOVED*** Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name conflict)
    key_metadata = Column("metadata", Text, nullable=True)  ***REMOVED*** JSON string for additional data
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_api_key_hash', 'key_hash'),
        Index('idx_api_key_company', 'company_id'),
        Index('idx_api_key_tier', 'tier'),
        Index('idx_api_key_active', 'is_active'),
        Index('idx_api_key_expires', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<APIKey(id={self.id}, key_prefix='{self.key_prefix}', company='{self.company}', tier='{self.tier}')>"
    
    def to_dict(self):
        """Convert API key to dictionary (without hash)"""
        return {
            "id": self.id,
            "key_prefix": self.key_prefix,
            "company": self.company,
            "company_id": self.company_id,
            "tier": self.tier,
            "quota_per_minute": self.quota_per_minute,
            "quota_per_day": self.quota_per_day,
            "quota_per_month": self.quota_per_month,
            "is_active": self.is_active,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }
