***REMOVED*** -*- coding: utf-8 -*-
"""
Persona Service - Persona pool creation service
Creates persona pool from platforms like LinkedIn
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.b2b_persona import Persona
from backend.models.b2b_company import Company
from backend.db import SessionLocal
from backend.services.b2b.decision_maker_service import decision_maker_service
import os
import requests


class PersonaService:
    """Persona pool creation and management service"""
    
    def __init__(self):
        self.linkedin_api_key = os.getenv("LINKEDIN_API_KEY")
        self.linkedin_api_secret = os.getenv("LINKEDIN_API_SECRET")
    
    def _get_db(self) -> Session:
        """Get database session"""
        return SessionLocal()
    
    def create_persona(
        self,
        company_id: int,
        full_name: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        job_title: Optional[str] = None,
        department: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        linkedin_profile_id: Optional[str] = None,
        source_platform: str = "linkedin",
        profile_data: Optional[Dict] = None,
        ***REMOVED*** Hyper-personalization fields
        work_location_address: Optional[str] = None,
        work_location_floor: Optional[str] = None,
        spouse_name: Optional[str] = None,
        spouse_occupation: Optional[str] = None,
        children_count: Optional[int] = None,
        children_info: Optional[List] = None,
        interests: Optional[List] = None,
        hobbies: Optional[List] = None,
        education: Optional[List] = None,
        alma_mater: Optional[str] = None,
        certifications: Optional[List] = None,
        previous_companies: Optional[List] = None,
        years_of_experience: Optional[int] = None,
        preferred_communication_method: Optional[str] = None,
        preferred_contact_time: Optional[str] = None,
        language_preferences: Optional[List] = None,
        hyper_personalization_data: Optional[Dict] = None
    ) -> Persona:
        """Create new persona"""
        db = self._get_db()
        try:
            ***REMOVED*** Split names
            if not first_name or not last_name:
                name_parts = full_name.split(" ", 1)
                first_name = name_parts[0] if len(name_parts) > 0 else ""
                last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            ***REMOVED*** Determine decision maker information
            classification = decision_maker_service.classify_persona(
                job_title=job_title,
                department=department
            )
            
            persona = Persona(
                company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=email,
            phone=phone,
            job_title=job_title,
            department=department,
            linkedin_url=linkedin_url,
            linkedin_profile_id=linkedin_profile_id,
            source_platform=source_platform,
            profile_url=linkedin_url,
            profile_data=profile_data or {},
            ***REMOVED*** Hyper-personalization fields
            work_location_address=work_location_address,
            work_location_floor=work_location_floor,
            spouse_name=spouse_name,
            spouse_occupation=spouse_occupation,
            children_count=children_count or 0,
            children_info=children_info or [],
            interests=interests or [],
            hobbies=hobbies or [],
            education=education or [],
            alma_mater=alma_mater,
            certifications=certifications or [],
            previous_companies=previous_companies or [],
            years_of_experience=years_of_experience,
            preferred_communication_method=preferred_communication_method,
            preferred_contact_time=preferred_contact_time,
            language_preferences=language_preferences or [],
            hyper_personalization_data=hyper_personalization_data or {},
            ***REMOVED*** Decision maker classification
            is_decision_maker=classification["is_decision_maker"],
            decision_maker_type=classification["decision_maker_type"],
            seniority_level=classification["seniority_level"],
            decision_authority=classification["decision_authority"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
            )
            
            db.add(persona)
            db.commit()
            db.refresh(persona)
            
            return persona
        finally:
            db.close()
    
    def search_linkedin_profiles(
        self,
        company_name: str,
        job_title_keywords: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search company employees on LinkedIn
        Note: This is a sample implementation. Real LinkedIn API integration
        requires LinkedIn API or third-party services (Apollo, Hunter.io, etc.).
        """
        ***REMOVED*** Sample structure for LinkedIn API integration
        ***REMOVED*** Real implementation should use LinkedIn API or third-party service
        
        ***REMOVED*** Sample response format
        ***REMOVED*** Real implementation will make LinkedIn API calls
        return []
    
    def fetch_linkedin_profile(self, profile_url: str) -> Optional[Dict]:
        """
        Fetch profile information from LinkedIn profile URL
        Note: This is a sample implementation. Real LinkedIn API integration is required.
        """
        ***REMOVED*** Fetch profile information with LinkedIn API or web scraping
        ***REMOVED*** Real implementation should use LinkedIn API or third-party service
        return None
    
    def import_personas_from_linkedin(
        self,
        company_id: int,
        company_name: str,
        job_title_keywords: Optional[List[str]] = None
    ) -> List[Persona]:
        """
        Import personas from LinkedIn
        """
        ***REMOVED*** Search profiles from LinkedIn
        profiles = self.search_linkedin_profiles(
            company_name=company_name,
            job_title_keywords=job_title_keywords
        )
        
        personas = []
        for profile in profiles:
            persona = self.create_persona(
                company_id=company_id,
                full_name=profile.get("full_name", ""),
                first_name=profile.get("first_name"),
                last_name=profile.get("last_name"),
                email=profile.get("email"),
                phone=profile.get("phone"),
                job_title=profile.get("job_title"),
                department=profile.get("department"),
                linkedin_url=profile.get("linkedin_url"),
                linkedin_profile_id=profile.get("linkedin_profile_id"),
                source_platform="linkedin",
                profile_data=profile.get("profile_data", {})
            )
            personas.append(persona)
        
        return personas
    
    def bulk_create_personas(self, personas_data: List[Dict]) -> List[Persona]:
        """Bulk create personas"""
        db = self._get_db()
        try:
            personas = []
            
            for data in personas_data:
                classification = decision_maker_service.classify_persona(
                    job_title=data.get("job_title"),
                    department=data.get("department")
                )
                
                ***REMOVED*** Split names
                full_name = data.get("full_name", "")
                name_parts = full_name.split(" ", 1)
                first_name = data.get("first_name") or (name_parts[0] if len(name_parts) > 0 else "")
                last_name = data.get("last_name") or (name_parts[1] if len(name_parts) > 1 else "")
                
                persona = Persona(
                    company_id=data.get("company_id"),
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    email=data.get("email"),
                    phone=data.get("phone"),
                    job_title=data.get("job_title"),
                    department=data.get("department"),
                    linkedin_url=data.get("linkedin_url"),
                    linkedin_profile_id=data.get("linkedin_profile_id"),
                    source_platform=data.get("source_platform", "manual"),
                    profile_url=data.get("profile_url") or data.get("linkedin_url"),
                    profile_data=data.get("profile_data", {}),
                    ***REMOVED*** Hyper-personalization fields
                    work_location_address=data.get("work_location_address"),
                    work_location_floor=data.get("work_location_floor"),
                    spouse_name=data.get("spouse_name"),
                    spouse_occupation=data.get("spouse_occupation"),
                    children_count=data.get("children_count", 0),
                    children_info=data.get("children_info", []),
                    interests=data.get("interests", []),
                    hobbies=data.get("hobbies", []),
                    education=data.get("education", []),
                    alma_mater=data.get("alma_mater"),
                    certifications=data.get("certifications", []),
                    previous_companies=data.get("previous_companies", []),
                    years_of_experience=data.get("years_of_experience"),
                    preferred_communication_method=data.get("preferred_communication_method"),
                    preferred_contact_time=data.get("preferred_contact_time"),
                    language_preferences=data.get("language_preferences", []),
                    hyper_personalization_data=data.get("hyper_personalization_data", {}),
                    ***REMOVED*** Decision maker classification
                    is_decision_maker=classification["is_decision_maker"],
                    decision_maker_type=classification["decision_maker_type"],
                    seniority_level=classification["seniority_level"],
                    decision_authority=classification["decision_authority"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                personas.append(persona)
                db.add(persona)
            
            db.commit()
            for persona in personas:
                db.refresh(persona)
            
            return personas
        finally:
            db.close()
    
    def get_personas_by_company(self, company_id: int) -> List[Persona]:
        """Get personas by company"""
        db = self._get_db()
        try:
            return db.query(Persona).filter(Persona.company_id == company_id).all()
        finally:
            db.close()
    
    def get_persona_by_id(self, persona_id: int) -> Optional[Persona]:
        """Get persona by ID"""
        db = self._get_db()
        try:
            return db.query(Persona).filter(Persona.id == persona_id).first()
        finally:
            db.close()
    
    def update_persona(self, persona_id: int, **kwargs) -> Optional[Persona]:
        """Update persona information"""
        db = self._get_db()
        try:
            persona = db.query(Persona).filter(Persona.id == persona_id).first()
            
            if not persona:
                return None
            
            for key, value in kwargs.items():
                if hasattr(persona, key) and value is not None:
                    setattr(persona, key, value)
            
            ***REMOVED*** Recalculate decision maker information if job_title or department is updated
            if "job_title" in kwargs or "department" in kwargs:
                classification = decision_maker_service.classify_persona(
                    job_title=persona.job_title,
                    department=persona.department
                )
                persona.is_decision_maker = classification["is_decision_maker"]
                persona.decision_maker_type = classification["decision_maker_type"]
                persona.seniority_level = classification["seniority_level"]
                persona.decision_authority = classification["decision_authority"]
            
            persona.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(persona)
            
            return persona
        finally:
            db.close()
    
    def get_persona_statistics(self, company_id: Optional[int] = None) -> Dict:
        """Get persona pool statistics"""
        db = self._get_db()
        try:
            query = db.query(Persona)
            
            if company_id:
                query = query.filter(Persona.company_id == company_id)
            
            all_personas = query.all()
            
            return {
                "total_personas": len(all_personas),
                "decision_makers": len([p for p in all_personas if p.is_decision_maker]),
                "with_email": len([p for p in all_personas if p.email]),
                "with_linkedin": len([p for p in all_personas if p.linkedin_url]),
                "by_source": {}
            }
        finally:
            db.close()


***REMOVED*** Global instance
persona_service = PersonaService()

