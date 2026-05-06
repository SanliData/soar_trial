"""
MODEL: discovery_record
PURPOSE: Discovery records model for company research results
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class DiscoveryRecord(Base):
    """
    Discovery record model for storing company research results.
    Each record is associated with a user.
    """
    
    __tablename__ = "discovery_records"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign key to User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    ***REMOVED*** Company information
    company_name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    website = Column(String(512), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    
    ***REMOVED*** Research metadata
    source = Column(String(255), nullable=True)  ***REMOVED*** "Google Search", "LinkedIn", etc.
    status = Column(String(50), nullable=True)  ***REMOVED*** "Verified", "Pending", etc.
    
    ***REMOVED*** Intelligence data (stored as JSON)
    industry = Column(String(255), nullable=True)
    employee_count = Column(String(100), nullable=True)
    technology_stack = Column(JSON, nullable=True)  ***REMOVED*** List of technologies
    business_activity = Column(Text, nullable=True)
    
    ***REMOVED*** Additional metadata
    research_data = Column(JSON, nullable=True)  ***REMOVED*** Full research response
    location_data = Column(JSON, nullable=True)  ***REMOVED*** Location/coordinates if available
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationship to User
    user = relationship("User", backref="discovery_records")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_discovery_user_id', 'user_id'),
        Index('idx_discovery_company_name', 'company_name'),
        Index('idx_discovery_status', 'status'),
    )
    
    def __repr__(self):
        return f"<DiscoveryRecord(id={self.id}, company_name='{self.company_name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """
        Convert discovery record to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "address": self.address,
            "website": self.website,
            "phone": self.phone,
            "email": self.email,
            "source": self.source,
            "status": self.status,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "technology_stack": self.technology_stack,
            "business_activity": self.business_activity,
            "research_data": self.research_data,
            "location_data": self.location_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


