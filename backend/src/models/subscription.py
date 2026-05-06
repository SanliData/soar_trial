"""
MODEL: subscription
PURPOSE: Subscription model for user plans and payments
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class Subscription(Base):
    """
    Subscription model for storing user account state and payment information.
    DEPRECATED: This model is being phased out in favor of UserAccount for usage-based pricing.
    Kept for backward compatibility during migration.
    """
    
    __tablename__ = "subscriptions"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    ***REMOVED*** Subscription plan (DEPRECATED - use UserAccount instead)
    plan_type = Column(String(50), default="usage_based", nullable=False, index=True)  ***REMOVED*** Legacy: "free", "pro", "enterprise", "usage_based"
    
    ***REMOVED*** Billing mode
    billing_mode = Column(String(50), default="usage_based", nullable=False)  ***REMOVED*** "usage_based" only
    
    ***REMOVED*** Payment information
    payment_provider = Column(String(50), nullable=True)  ***REMOVED*** "stripe", "iyzico", etc.
    payment_customer_id = Column(String(255), nullable=True, index=True)  ***REMOVED*** Stripe/Iyzico customer ID
    payment_subscription_id = Column(String(255), nullable=True, index=True)  ***REMOVED*** Stripe/Iyzico subscription ID
    
    ***REMOVED*** Subscription status
    status = Column(String(50), default="active", nullable=False, index=True)  ***REMOVED*** "active", "cancelled", "expired", "past_due"
    
    ***REMOVED*** Billing information
    billing_cycle = Column(String(20), nullable=True)  ***REMOVED*** "monthly", "yearly"
    price = Column(Float, nullable=True)  ***REMOVED*** Subscription price
    currency = Column(String(10), default="USD", nullable=False)  ***REMOVED*** Currency code
    
    ***REMOVED*** Dates
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True, index=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    trial_started_at = Column(DateTime(timezone=True), nullable=True)  ***REMOVED*** When trial started
    
    ***REMOVED*** Features (stored as JSON for flexibility)
    features = Column(String, nullable=True)  ***REMOVED*** JSON string of enabled features
    
    ***REMOVED*** Usage-based pricing base subscription
    base_subscription_price = Column(Float, default=0.98, nullable=True)  ***REMOVED*** $0.98/month base fee for usage-based
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="subscription", uselist=False)
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_subscription_user_id', 'user_id'),
        Index('idx_subscription_plan_type', 'plan_type'),
        Index('idx_subscription_status', 'status'),
        Index('idx_subscription_period_end', 'current_period_end'),
    )
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan_type='{self.plan_type}', status='{self.status}')>"
    
    def to_dict(self):
        """
        Convert subscription to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan_type": self.plan_type,
            "payment_provider": self.payment_provider,
            "payment_customer_id": self.payment_customer_id,
            "payment_subscription_id": self.payment_subscription_id,
            "status": self.status,
            "billing_cycle": self.billing_cycle,
            "price": self.price,
            "currency": self.currency,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "current_period_start": self.current_period_start.isoformat() if self.current_period_start else None,
            "current_period_end": self.current_period_end.isoformat() if self.current_period_end else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "trial_end": self.trial_end.isoformat() if self.trial_end else None,
            "trial_started_at": self.trial_started_at.isoformat() if self.trial_started_at else None,
            "billing_mode": getattr(self, 'billing_mode', 'subscription'),
            "base_subscription_price": getattr(self, 'base_subscription_price', None),
            "features": self.features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        from datetime import datetime
        if self.status != "active":
            return False
        if self.current_period_end:
            return datetime.utcnow() < self.current_period_end
        return True
    
    def is_trial_active(self) -> bool:
        """Check if trial period is active."""
        from datetime import datetime
        if self.trial_end:
            return datetime.utcnow() < self.trial_end
        return False


