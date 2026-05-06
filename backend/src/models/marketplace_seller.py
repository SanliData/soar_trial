"""
MODEL: marketplace_seller
PURPOSE: Marketplace seller model for online seller discovery
ENCODING: UTF-8 WITHOUT BOM

Stores marketplace seller information (Amazon, eBay, Etsy, etc.)
with inferred business entity and owner data.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class MarketplaceSeller(Base):
    """
    Marketplace seller model for online seller discovery.
    Supports multiple marketplaces (Amazon, eBay, Etsy, etc.)
    with business entity and owner inference.
    """
    
    __tablename__ = "marketplace_sellers"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User (who discovered this seller)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Marketplace information
    marketplace = Column(String(50), nullable=False, index=True)   # "amazon", "ebay", "etsy", "ali express", "trendyol", "hepsiburada"
    seller_id = Column(String(255), nullable=False, index=True)   # Platform-specific seller ID
    seller_name = Column(String(255), nullable=False)   # Display name on marketplace
    seller_profile_url = Column(String(512), nullable=True)   # URL to seller profile
    
    # Business entity (inferred)
    business_name = Column(String(255), nullable=True, index=True)   # Inferred business name
    business_registration_number = Column(String(100), nullable=True)   # Tax ID, registration number, etc.
    business_address = Column(Text, nullable=True)   # Inferred business address
    business_location = Column(JSON, nullable=True)   # Coordinates {lat, lng}
    
    # Owner inference
    owner_inference = Column(JSON, nullable=True)   # Inferred owner data
    # Format: {
    # "name": "John Doe",
    # "email": "john@example.com",
    # "confidence": 0.75,
    # "sources": ["public records", "website", "social media"]
    # }
    
    # Location inference
    location_inference_confidence = Column(Float, nullable=True)   # 0.0 to 1.0
    location_signals = Column(JSON, nullable=True)   # Location signals extracted
    
    # Seller metadata
    seller_metadata = Column(JSON, nullable=True)   # Additional seller data from marketplace
    # Format: {
    # "rating": 4.8,
    # "review_count": 1250,
    # "joined_date": "2020-01-15",
    # "product_categories": ["Electronics", "Home"],
    # "total_sales": 50000
    # }
    
    # Status
    status = Column(String(50), default="active", nullable=False)   # "active", "inactive", "archived"
    verification_status = Column(String(50), nullable=True)   # "verified", "pending", "unverified"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="marketplace_sellers")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_marketplace_seller_user_id', 'user_id'),
        Index('idx_marketplace_seller_marketplace', 'marketplace'),
        Index('idx_marketplace_seller_seller_id', 'seller_id'),
        Index('idx_marketplace_seller_business_name', 'business_name'),
        Index('idx_marketplace_seller_marketplace_id', 'marketplace', 'seller_id'),   # Unique constraint per marketplace
    )
    
    def __repr__(self):
        return f"<MarketplaceSeller(id={self.id}, marketplace='{self.marketplace}', seller_id='{self.seller_id}', seller_name='{self.seller_name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "marketplace": self.marketplace,
            "seller_id": self.seller_id,
            "seller_name": self.seller_name,
            "seller_profile_url": self.seller_profile_url,
            "business_name": self.business_name,
            "business_registration_number": self.business_registration_number,
            "business_address": self.business_address,
            "business_location": self.business_location,
            "owner_inference": self.owner_inference,
            "location_inference_confidence": self.location_inference_confidence,
            "location_signals": self.location_signals,
            "seller_metadata": self.seller_metadata,
            "status": self.status,
            "verification_status": self.verification_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
