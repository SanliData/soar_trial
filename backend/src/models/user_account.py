"""
MODEL: user_account
PURPOSE: User account state for usage-based pricing
ENCODING: UTF-8 WITHOUT BOM

Tracks account activation, usage caps, and billing state.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship
from src.db.base import Base


class UserAccount(Base):
    """
    User account model for usage-based pricing.
    Replaces fixed subscription tiers with account state tracking.
    """
    
    __tablename__ = "user_accounts"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    ***REMOVED*** Account status
    account_status = Column(String(50), default="inactive", nullable=False, index=True)  ***REMOVED*** "inactive", "active", "suspended"
    
    ***REMOVED*** Activation fee payment
    activation_fee_paid = Column(Boolean, default=False, nullable=False)
    activation_fee_paid_at = Column(DateTime(timezone=True), nullable=True)
    activation_fee_next_due = Column(DateTime(timezone=True), nullable=True)  ***REMOVED*** Next monthly due date
    
    ***REMOVED*** Query cap (non-negotiable unless admin override)
    query_cap = Column(Integer, default=100, nullable=False)  ***REMOVED*** MAX 100 results per query
    admin_override_active = Column(Boolean, default=False, nullable=False)  ***REMOVED*** Admin override for higher caps
    admin_override_cap = Column(Integer, nullable=True)  ***REMOVED*** Override cap (max 1000)
    
    ***REMOVED*** Usage tracking (references usage_tracking table)
    ***REMOVED*** Total queries executed this month
    queries_this_month = Column(Integer, default=0, nullable=False)
    queries_last_reset = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    ***REMOVED*** Billing information
    currency = Column(String(10), default="USD", nullable=False)
    payment_provider = Column(String(50), nullable=True)  ***REMOVED*** "stripe", "iyzico", etc.
    payment_customer_id = Column(String(255), nullable=True, index=True)
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship
    user = relationship("User", backref="account", uselist=False)
    
    ***REMOVED*** Indexes
    __table_args__ = (
        Index('idx_user_account_user_id', 'user_id'),
        Index('idx_user_account_status', 'account_status'),
        Index('idx_user_account_activation_due', 'activation_fee_next_due'),
    )
    
    def __repr__(self):
        return f"<UserAccount(id={self.id}, user_id={self.user_id}, status='{self.account_status}')>"
    
    def to_dict(self):
        """Convert account to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "account_status": self.account_status,
            "activation_fee_paid": self.activation_fee_paid,
            "activation_fee_paid_at": self.activation_fee_paid_at.isoformat() if self.activation_fee_paid_at else None,
            "activation_fee_next_due": self.activation_fee_next_due.isoformat() if self.activation_fee_next_due else None,
            "query_cap": self.query_cap,
            "admin_override_active": self.admin_override_active,
            "admin_override_cap": self.admin_override_cap,
            "queries_this_month": self.queries_this_month,
            "queries_last_reset": self.queries_last_reset.isoformat() if self.queries_last_reset else None,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_active(self) -> bool:
        """Check if account is active."""
        return self.account_status == "active" and self.activation_fee_paid
    
    def get_effective_query_cap(self) -> int:
        """Get effective query cap (respects admin override)."""
        if self.admin_override_active and self.admin_override_cap:
            return self.admin_override_cap
        return self.query_cap
