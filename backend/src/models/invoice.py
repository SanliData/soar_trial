"""
MODEL: invoice
PURPOSE: Invoice and payment history model
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Invoice(Base):
    """
    Invoice model for storing payment history and invoices.
    """
    
    __tablename__ = "invoices"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Foreign key to Subscription
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True, index=True)
    
    # Invoice information
    invoice_number = Column(String(100), nullable=False, unique=True, index=True)
    payment_provider = Column(String(50), nullable=False)   # "stripe", "iyzico"
    payment_provider_invoice_id = Column(String(255), nullable=True, index=True)   # Stripe invoice ID
    
    # Amount information
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD", nullable=False)
    tax_amount = Column(Float, default=0.0, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String(50), default="pending", nullable=False, index=True)   # "pending", "paid", "failed", "refunded"
    
    # Payment information
    paid_at = Column(DateTime(timezone=True), nullable=True)
    payment_method = Column(String(50), nullable=True)   # "card", "bank_transfer", etc.
    
    # Billing period
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    invoice_metadata = Column(JSON, nullable=True)   # Additional invoice data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="invoices")
    subscription = relationship("Subscription", backref="invoices")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_invoice_user_id', 'user_id'),
        Index('idx_invoice_subscription_id', 'subscription_id'),
        Index('idx_invoice_status', 'status'),
        Index('idx_invoice_created_at', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', user_id={self.user_id}, amount={self.total_amount}, status='{self.status}')>"
    
    def to_dict(self):
        """
        Convert invoice to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "subscription_id": self.subscription_id,
            "invoice_number": self.invoice_number,
            "payment_provider": self.payment_provider,
            "payment_provider_invoice_id": self.payment_provider_invoice_id,
            "amount": self.amount,
            "currency": self.currency,
            "tax_amount": self.tax_amount,
            "total_amount": self.total_amount,
            "status": self.status,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "payment_method": self.payment_method,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "metadata": self.invoice_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

