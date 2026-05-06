***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Persona Model - Decision maker individuals (from LinkedIn, etc. platforms)
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db import Base


class Persona(Base):
    """Target decision maker individual profile"""
    __tablename__ = "b2b_personas"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("b2b_companies.id"), nullable=False, index=True)
    
    ***REMOVED*** Personal information
    first_name = Column(String(100))
    last_name = Column(String(100))
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), index=True)
    phone = Column(String(50))
    
    ***REMOVED*** Job information
    job_title = Column(String(255), index=True)  ***REMOVED*** Purchasing Manager, R&D Director, Owner, etc.
    department = Column(String(255))  ***REMOVED*** Purchasing, R&D, Management, etc.
    seniority_level = Column(String(50))  ***REMOVED*** C-Level, Director, Manager, Senior, etc.
    
    ***REMOVED*** Decision maker categories
    is_decision_maker = Column(Boolean, default=False, index=True)
    decision_maker_type = Column(String(100))  ***REMOVED*** purchasing, rnd, owner, finance, operations, etc.
    decision_authority = Column(String(50))  ***REMOVED*** high, medium, low
    
    ***REMOVED*** Platform information
    linkedin_url = Column(String(500))
    linkedin_profile_id = Column(String(100))
    source_platform = Column(String(50), default="linkedin")  ***REMOVED*** linkedin, apollo, hunter, etc.
    profile_url = Column(String(500))
    
    ***REMOVED*** Work location information (for hyper-personalization)
    work_location_address = Column(String(500))  ***REMOVED*** Specific work address
    work_location_latitude = Column(Float)
    work_location_longitude = Column(Float)
    work_location_floor = Column(String(50))  ***REMOVED*** Floor/office number
    work_location_department_floor = Column(String(100))  ***REMOVED*** Department floor/area
    
    ***REMOVED*** Personal information (for hyper-personalization)
    spouse_name = Column(String(255))  ***REMOVED*** Spouse name
    spouse_occupation = Column(String(255))  ***REMOVED*** Spouse occupation
    children_count = Column(Integer, default=0)
    children_info = Column(JSON, default=list)  ***REMOVED*** [{"name": "...", "age": 10, "school": "..."}]
    
    ***REMOVED*** Interests and hobbies
    interests = Column(JSON, default=list)  ***REMOVED*** ["golf", "reading", "travel"]
    hobbies = Column(JSON, default=list)  ***REMOVED*** ["photography", "cooking"]
    social_media_profiles = Column(JSON, default=dict)  ***REMOVED*** {"twitter": "...", "instagram": "..."}
    
    ***REMOVED*** Education information
    education = Column(JSON, default=list)  ***REMOVED*** [{"school": "...", "degree": "...", "field": "...", "year": 2010}]
    alma_mater = Column(String(255))  ***REMOVED*** Primary alma mater
    certifications = Column(JSON, default=list)  ***REMOVED*** Professional certifications
    
    ***REMOVED*** Professional background
    previous_companies = Column(JSON, default=list)  ***REMOVED*** Previous work history
    years_of_experience = Column(Integer)
    industry_experience_years = Column(Integer)
    
    ***REMOVED*** Personal preferences (for hyper-personalization)
    preferred_communication_method = Column(String(50))  ***REMOVED*** email, phone, linkedin, in_person
    preferred_contact_time = Column(String(100))  ***REMOVED*** "morning", "afternoon", "weekdays"
    language_preferences = Column(JSON, default=list)  ***REMOVED*** ["Turkish", "English"]
    
    ***REMOVED*** Behavioral data
    decision_making_style = Column(String(50))  ***REMOVED*** analytical, intuitive, collaborative, etc.
    risk_tolerance = Column(String(50))  ***REMOVED*** low, medium, high
    budget_authority = Column(String(50))  ***REMOVED*** none, small, medium, large
    
    ***REMOVED*** Metadata
    profile_data = Column(JSON, default=dict)  ***REMOVED*** LinkedIn profile data, experience, education, etc.
    hyper_personalization_data = Column(JSON, default=dict)  ***REMOVED*** Additional hyper-personalization data
    verified = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    ***REMOVED*** Relationships
    company = relationship("Company", back_populates="personas")
    campaigns = relationship("Campaign", back_populates="target_persona", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="persona", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "job_title": self.job_title,
            "department": self.department,
            "seniority_level": self.seniority_level,
            "is_decision_maker": self.is_decision_maker,
            "decision_maker_type": self.decision_maker_type,
            "decision_authority": self.decision_authority,
            "linkedin_url": self.linkedin_url,
            "linkedin_profile_id": self.linkedin_profile_id,
            "source_platform": self.source_platform,
            "profile_url": self.profile_url,
            ***REMOVED*** Work location (hyper-personalization)
            "work_location": {
                "address": self.work_location_address,
                "latitude": self.work_location_latitude,
                "longitude": self.work_location_longitude,
                "floor": self.work_location_floor,
                "department_floor": self.work_location_department_floor,
            },
            ***REMOVED*** Personal information (hyper-personalization)
            "personal": {
                "spouse_name": self.spouse_name,
                "spouse_occupation": self.spouse_occupation,
                "children_count": self.children_count,
                "children_info": self.children_info or [],
            },
            ***REMOVED*** Interests and hobbies
            "interests": self.interests or [],
            "hobbies": self.hobbies or [],
            "social_media_profiles": self.social_media_profiles or {},
            ***REMOVED*** Education
            "education": self.education or [],
            "alma_mater": self.alma_mater,
            "certifications": self.certifications or [],
            ***REMOVED*** Professional background
            "previous_companies": self.previous_companies or [],
            "years_of_experience": self.years_of_experience,
            "industry_experience_years": self.industry_experience_years,
            ***REMOVED*** Preferences
            "preferences": {
                "communication_method": self.preferred_communication_method,
                "contact_time": self.preferred_contact_time,
                "languages": self.language_preferences or [],
            },
            ***REMOVED*** Behavioral data
            "behavioral": {
                "decision_making_style": self.decision_making_style,
                "risk_tolerance": self.risk_tolerance,
                "budget_authority": self.budget_authority,
            },
            ***REMOVED*** Metadata
            "profile_data": self.profile_data or {},
            "hyper_personalization_data": self.hyper_personalization_data or {},
            "verified": self.verified,
            "verification_date": self.verification_date.isoformat() if self.verification_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

