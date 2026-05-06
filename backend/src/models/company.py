"""
MODEL: company
PURPOSE: Company model for target companies
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Company(Base):
    """
    Company model for storing target companies.
    Each company is associated with a user.
    """
    
    __tablename__ = "companies"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    ***REMOVED*** Company information
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    website = Column(String(512), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    ***REMOVED*** Business information
    industry = Column(String(255), nullable=True)
    employee_count = Column(String(100), nullable=True)
    revenue = Column(String(100), nullable=True)
    
    ***REMOVED*** Additional data
    company_metadata = Column(JSON, nullable=True)  ***REMOVED*** Additional company data
    location_data = Column(JSON, nullable=True)  ***REMOVED*** Location/coordinates
    
    ***REMOVED*** Status
    status = Column(String(50), default="active", nullable=False)  ***REMOVED*** "active", "inactive", "archived", "won"
    cycle_status = Column(String(50), nullable=True)  ***REMOVED*** "pending", "targeted", "contacted", "converted", "won"
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="companies")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_company_user_id', 'user_id'),
        Index('idx_company_name', 'name'),
        Index('idx_company_industry', 'industry'),
    )
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """
        Convert company to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "address": self.address,
            "website": self.website,
            "phone": self.phone,
            "email": self.email,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "revenue": self.revenue,
            "metadata": self.company_metadata,
            "location_data": self.location_data,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

