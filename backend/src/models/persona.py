"""
MODEL: persona
PURPOSE: Persona model for target personnel/decision-makers
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index, Float
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.base import Base


class Persona(Base):
    """
    Persona model for storing target personnel/decision-makers.
    Each persona is associated with a user and optionally a company.
    """
    
    __tablename__ = "personas"
    
    ***REMOVED*** Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    ***REMOVED*** Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    
    ***REMOVED*** Personal information
    full_name = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    ***REMOVED*** Professional information
    job_title = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    seniority_level = Column(String(100), nullable=True)  ***REMOVED*** "C-Level", "Director", "Manager", etc.
    
    ***REMOVED*** Work location
    work_address = Column(Text, nullable=True)
    work_location = Column(JSON, nullable=True)  ***REMOVED*** Coordinates
    
    ***REMOVED*** Location Affinity (First-Class Attribute)
    location_affinity_score = Column(Float, nullable=True)  ***REMOVED*** 0.0 to 1.0
    location_signals = Column(JSON, nullable=True)  ***REMOVED*** List of location signals: ["urban", "coastal", "industrial", etc.]
    location_radius_meters = Column(Integer, nullable=True)  ***REMOVED*** Radius in meters for circular targeting
    location_polygon = Column(JSON, nullable=True)  ***REMOVED*** GeoJSON polygon for custom area targeting
    location_proximity_clusters = Column(JSON, nullable=True)  ***REMOVED*** List of cluster IDs for proximity grouping
    
    ***REMOVED*** Personal details (hyper-personalization)
    spouse_name = Column(String(255), nullable=True)
    children_info = Column(JSON, nullable=True)  ***REMOVED*** List of children names/ages
    interests = Column(JSON, nullable=True)  ***REMOVED*** List of interests
    education = Column(JSON, nullable=True)  ***REMOVED*** Education history
    professional_history = Column(JSON, nullable=True)  ***REMOVED*** Work history
    preferences = Column(JSON, nullable=True)  ***REMOVED*** Preferences
    behavioral_data = Column(JSON, nullable=True)  ***REMOVED*** Behavioral data
    
    ***REMOVED*** Social media
    linkedin_url = Column(String(512), nullable=True)
    profile_picture = Column(String(512), nullable=True)
    
    ***REMOVED*** Additional data
    persona_metadata = Column(JSON, nullable=True)  ***REMOVED*** Additional persona data
    
    ***REMOVED*** Status
    status = Column(String(50), default="active", nullable=False)  ***REMOVED*** "active", "inactive", "archived"
    
    ***REMOVED*** Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    ***REMOVED*** Relationships
    user = relationship("User", backref="personas")
    company = relationship("Company", backref="personas")
    
    ***REMOVED*** Indexes for performance
    __table_args__ = (
        Index('idx_persona_user_id', 'user_id'),
        Index('idx_persona_company_id', 'company_id'),
        Index('idx_persona_name', 'full_name'),
        Index('idx_persona_job_title', 'job_title'),
        Index('idx_persona_location_affinity', 'location_affinity_score'),  ***REMOVED*** For location-based queries
    )
    
    def __repr__(self):
        return f"<Persona(id={self.id}, full_name='{self.full_name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """
        Convert persona to dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "job_title": self.job_title,
            "department": self.department,
            "seniority_level": self.seniority_level,
            "work_address": self.work_address,
            "work_location": self.work_location,
            "location_affinity_score": self.location_affinity_score,
            "location_signals": self.location_signals,
            "location_radius_meters": self.location_radius_meters,
            "location_polygon": self.location_polygon,
            "location_proximity_clusters": self.location_proximity_clusters,
            "spouse_name": self.spouse_name,
            "children_info": self.children_info,
            "interests": self.interests,
            "education": self.education,
            "professional_history": self.professional_history,
            "preferences": self.preferences,
            "behavioral_data": self.behavioral_data,
            "linkedin_url": self.linkedin_url,
            "profile_picture": self.profile_picture,
            "metadata": self.persona_metadata,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

