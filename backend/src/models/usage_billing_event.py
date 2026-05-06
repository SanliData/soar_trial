"""
MODEL: usage_billing_event
PURPOSE: Track individual usage events for AWS-style billing
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Index, Text
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class UsageBillingEvent(Base):
    """
    Track individual usage events for usage-based billing.
    Each event represents a billable operation.
    """
    
    __tablename__ = "usage_billing_events"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    ***REMOVED*** Event type (verified_company, decision_maker_match, persona_enrichment, etc.)
    event_type = Column(String(100), nullable=False, index=True)
    
    ***REMOVED*** Billing period (YYYY-MM format)
    billing_period = Column(String(7), nullable=False, index=True)  ***REMOVED*** e.g., "2025-01"
    
    ***REMOVED*** Pricing information
    unit_price = Column(Float, nullable=False)  ***REMOVED*** Price per unit
    quantity = Column(Integer, default=1, nullable=False)  ***REMOVED*** Quantity (usually 1)
    total_cost = Column(Float, nullable=False)  ***REMOVED*** unit_price * quantity
    
    ***REMOVED*** Currency
    currency = Column(String(10), default="USD", nullable=False)
    
    ***REMOVED*** Metadata
    event_metadata = Column("metadata", JSON, nullable=True)  ***REMOVED*** Additional event data (company_id, persona_id, etc.)
    
    ***REMOVED*** Related entity IDs (optional)
    company_id = Column(Integer, nullable=True, index=True)
    persona_id = Column(Integer, nullable=True, index=True)
    campaign_id = Column(Integer, nullable=True, index=True)
    
    ***REMOVED*** Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="usage_billing_events")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_usage_billing_user_period', 'user_id', 'billing_period'),
        Index('idx_usage_billing_event_type', 'event_type'),
        Index('idx_usage_billing_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<UsageBillingEvent(id={self.id}, user_id={self.user_id}, event_type='{self.event_type}', cost={self.total_cost})>"
    
    def to_dict(self):
        """Convert usage billing event to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "billing_period": self.billing_period,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "total_cost": self.total_cost,
            "currency": self.currency,
            "metadata": self.metadata,
            "company_id": self.company_id,
            "persona_id": self.persona_id,
            "campaign_id": self.campaign_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
