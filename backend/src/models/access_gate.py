"""
MODEL: access_gate
PURPOSE: Purchase gating logic to control access to personal data
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Index, Boolean
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class AccessGate(Base):
    """
    Access gate model for controlling data access based on purchase.
    Locks personal data behind purchase actions, logs usage for billing.
    """
    
    __tablename__ = "access_gates"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feasibility_report_id = Column(Integer, ForeignKey("feasibility_reports.id"), nullable=True, index=True)
    
    # Access control
    module_type = Column(String(100), nullable=False, index=True)   # "feasibility", "exposure", "outreach", "contact_data"
    is_unlocked = Column(Boolean, default=False, nullable=False, index=True)   # Access gate status
    
    # Purchase reference
    purchase_id = Column(String(255), nullable=True, index=True)   # Purchase/subscription ID
    purchase_timestamp = Column(DateTime(timezone=True), nullable=True)   # When access was purchased
    
    # Usage tracking for billing
    access_count = Column(Integer, default=0, nullable=False)   # Number of times data accessed
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)   # Last access timestamp
    
    # Usage limits (based on subscription)
    usage_limit = Column(Integer, nullable=True)   # Access limit (null = unlimited)
    usage_reset_at = Column(DateTime(timezone=True), nullable=True)   # When usage resets
    
    # Metadata
    access_metadata = Column(JSON, nullable=True)   # Additional access control metadata
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="access_gates")
    feasibility_report = relationship("FeasibilityReport", backref="access_gates")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_gate_user_id', 'user_id'),
        Index('idx_gate_module_type', 'module_type'),
        Index('idx_gate_unlocked', 'is_unlocked'),
        Index('idx_gate_purchase_id', 'purchase_id'),
    )
    
    def __repr__(self):
        return f"<AccessGate(id={self.id}, module_type='{self.module_type}', is_unlocked={self.is_unlocked})>"
    
    def to_dict(self):
        """Convert access gate to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "feasibility_report_id": self.feasibility_report_id,
            "module_type": self.module_type,
            "is_unlocked": self.is_unlocked,
            "purchase_id": self.purchase_id,
            "purchase_timestamp": self.purchase_timestamp.isoformat() if self.purchase_timestamp else None,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "usage_limit": self.usage_limit,
            "usage_reset_at": self.usage_reset_at.isoformat() if self.usage_reset_at else None,
            "access_metadata": self.access_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
