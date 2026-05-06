***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Product Model - Product definition and management
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base


class Product(Base):
    """Product definition for B2B sales"""
    __tablename__ = "b2b_products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)  ***REMOVED*** Product owner
    
    ***REMOVED*** Product information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(255))  ***REMOVED*** Product category
    subcategory = Column(String(255))
    
    ***REMOVED*** Product understanding (AI analysis results)
    ai_analysis = Column(JSON, default=dict)  ***REMOVED*** AI analysis results
    use_cases = Column(JSON, default=list)  ***REMOVED*** List of use cases
    target_industries = Column(JSON, default=list)  ***REMOVED*** Target industries identified by AI
    product_features = Column(JSON, default=list)  ***REMOVED*** Product features
    
    ***REMOVED*** Status
    status = Column(String(50), default="draft")  ***REMOVED*** draft, analyzed, active, archived
    analyzed_at = Column(DateTime)
    
    ***REMOVED*** Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, default=dict)
    
    ***REMOVED*** Relationships
    companies = relationship("Company", back_populates="product", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "subcategory": self.subcategory,
            "ai_analysis": self.ai_analysis or {},
            "use_cases": self.use_cases or [],
            "target_industries": self.target_industries or [],
            "product_features": self.product_features or [],
            "status": self.status,
            "analyzed_at": self.analyzed_at.isoformat() if self.analyzed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata or {},
        }

