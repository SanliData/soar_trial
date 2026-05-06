"""
MODEL: product
PURPOSE: Product model for product definitions
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Product(Base):
    """
    Product model for storing product definitions.
    Each product is associated with a user.
    """
    
    __tablename__ = "products"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Product information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    
    # Identification
    identification_type = Column(String(50), nullable=False)   # "name", "barcode", "qrcode", "giftcode"
    code = Column(String(255), nullable=True)   # Barcode, QR code, or gift code
    
    # Additional data
    product_metadata = Column(JSON, nullable=True)   # Additional product data
    image_url = Column(String(512), nullable=True)   # Product image URL
    
    # Status
    status = Column(String(50), default="active", nullable=False)   # "active", "inactive", "archived"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship to User
    user = relationship("User", backref="products")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_product_user_id', 'user_id'),
        Index('idx_product_name', 'name'),
        Index('idx_product_code', 'code'),
    )
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """
        Convert product to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "identification_type": self.identification_type,
            "code": self.code,
            "metadata": self.product_metadata,
            "image_url": self.image_url,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

