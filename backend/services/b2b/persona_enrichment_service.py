***REMOVED*** -*- coding: utf-8 -*-
"""
Persona Enrichment Service - Hyper-personalization data enrichment
Collects detailed information from open sources for hyper-personalization
"""

from typing import List, Dict, Optional
from backend.models.b2b_persona import Persona
from backend.services.b2b.persona_service import persona_service
from backend.services.b2b.address_validation_service import address_validation_service
import os
from backend.services.openai_client import OpenAIVisionClient
import requests


class PersonaEnrichmentService:
    """Enrich persona data with hyper-personalization information from open sources"""
    
    def __init__(self):
        self.openai_client = OpenAIVisionClient() if os.getenv("OPENAI_API_KEY") else None
        self.linkedin_api_key = os.getenv("LINKEDIN_API_KEY")
    
    def enrich_persona_from_linkedin(self, persona_id: int) -> Persona:
        """
        Enrich persona with detailed information from LinkedIn
        - Education (schools, degrees)
        - Work history
        - Interests and activities
        - Connections and network
        """
        persona = persona_service.get_persona_by_id(persona_id)
        if not persona:
            raise ValueError("Persona not found")
        
        if not persona.linkedin_url:
            return persona
        
        ***REMOVED*** Fetch LinkedIn profile data
        linkedin_data = self._fetch_linkedin_profile_data(persona.linkedin_url)
        
        if linkedin_data:
            ***REMOVED*** Extract education
            if "education" in linkedin_data:
                persona.education = linkedin_data["education"]
                if linkedin_data["education"]:
                    persona.alma_mater = linkedin_data["education"][0].get("school", "")
            
            ***REMOVED*** Extract work history
            if "experience" in linkedin_data:
                persona.previous_companies = linkedin_data["experience"]
                persona.years_of_experience = self._calculate_years_of_experience(linkedin_data["experience"])
            
            ***REMOVED*** Extract interests
            if "interests" in linkedin_data:
                persona.interests = linkedin_data["interests"]
            
            ***REMOVED*** Extract certifications
            if "certifications" in linkedin_data:
                persona.certifications = linkedin_data["certifications"]
            
            ***REMOVED*** Extract social media
            if "social_media" in linkedin_data:
                persona.social_media_profiles = linkedin_data["social_media"]
            
            ***REMOVED*** Update profile data
            persona.profile_data = {**persona.profile_data, **linkedin_data}
            
            ***REMOVED*** Save
            persona_service.update_persona(persona_id, **{
                "education": persona.education,
                "alma_mater": persona.alma_mater,
                "previous_companies": persona.previous_companies,
                "years_of_experience": persona.years_of_experience,
                "interests": persona.interests,
                "certifications": persona.certifications,
                "social_media_profiles": persona.social_media_profiles,
                "profile_data": persona.profile_data
            })
        
        return persona
    
    def enrich_persona_from_open_sources(self, persona_id: int) -> Persona:
        """
        Enrich persona from multiple open sources:
        - LinkedIn
        - Public records
        - Social media
        - Company websites
        - News articles
        """
        persona = persona_service.get_persona_by_id(persona_id)
        if not persona:
            raise ValueError("Persona not found")
        
        ***REMOVED*** 1. LinkedIn enrichment
        if persona.linkedin_url:
            persona = self.enrich_persona_from_linkedin(persona_id)
        
        ***REMOVED*** 2. Work location enrichment
        persona = self._enrich_work_location(persona)
        
        ***REMOVED*** 3. Personal information (spouse, children) - from public sources
        persona = self._enrich_personal_info(persona)
        
        ***REMOVED*** 4. Behavioral analysis
        persona = self._analyze_behavioral_data(persona)
        
        return persona
    
    def _fetch_linkedin_profile_data(self, linkedin_url: str) -> Optional[Dict]:
        """
        Fetch LinkedIn profile data
        Note: Real implementation requires LinkedIn API or web scraping
        """
        ***REMOVED*** Placeholder - real implementation would use LinkedIn API
        ***REMOVED*** or web scraping with proper rate limiting and respect for ToS
        return None
    
    def _enrich_work_location(self, persona: Persona) -> Persona:
        """Enrich work location with specific floor/office information"""
        ***REMOVED*** Get company location
        from backend.services.b2b.customer_pool_service import customer_pool_service
        company = customer_pool_service.get_company_by_id(persona.company_id)
        
        if company and company.latitude and company.longitude:
            ***REMOVED*** Use company location as base
            persona.work_location_address = company.address_line1
            persona.work_location_latitude = company.latitude
            persona.work_location_longitude = company.longitude
            
            ***REMOVED*** Try to get more specific location (floor, department) from company website or other sources
            ***REMOVED*** This would require web scraping or company directory lookup
            persona.work_location_floor = None  ***REMOVED*** Would be populated from sources
            persona.work_location_department_floor = None
        
        return persona
    
    def _enrich_personal_info(self, persona: Persona) -> Persona:
        """
        Enrich personal information (spouse, children) from open sources
        Note: This requires careful handling of privacy and data protection laws
        """
        ***REMOVED*** This would use:
        ***REMOVED*** - Public records (if legally accessible)
        ***REMOVED*** - Social media (public posts)
        ***REMOVED*** - News articles
        ***REMOVED*** - Company announcements
        
        ***REMOVED*** Example: AI analysis of public information
        if self.openai_client and persona.full_name:
            ***REMOVED*** Use AI to analyze public information (if available)
            ***REMOVED*** This is a placeholder - real implementation would need proper data sources
            pass
        
        return persona
    
    def _analyze_behavioral_data(self, persona: Persona) -> Persona:
        """Analyze behavioral data from profile information"""
        ***REMOVED*** Analyze decision making style from job title and experience
        if persona.job_title:
            title_lower = persona.job_title.lower()
            if "analyst" in title_lower or "data" in title_lower:
                persona.decision_making_style = "analytical"
            elif "director" in title_lower or "manager" in title_lower:
                persona.decision_making_style = "collaborative"
            else:
                persona.decision_making_style = "intuitive"
        
        ***REMOVED*** Risk tolerance based on industry and role
        if persona.decision_maker_type == "owner" or persona.seniority_level == "c_level":
            persona.risk_tolerance = "high"
        elif persona.seniority_level == "director":
            persona.risk_tolerance = "medium"
        else:
            persona.risk_tolerance = "low"
        
        ***REMOVED*** Budget authority based on role
        if persona.decision_authority == "high":
            persona.budget_authority = "large"
        elif persona.decision_authority == "medium":
            persona.budget_authority = "medium"
        else:
            persona.budget_authority = "small"
        
        return persona
    
    def _calculate_years_of_experience(self, experience: List[Dict]) -> Optional[int]:
        """Calculate total years of experience from work history"""
        if not experience:
            return None
        
        total_years = 0
        for exp in experience:
            start_year = exp.get("start_year")
            end_year = exp.get("end_year") or 2024  ***REMOVED*** Current year if ongoing
            if start_year:
                total_years += (end_year - start_year)
        
        return total_years if total_years > 0 else None
    
    def add_hyper_personalization_data(
        self,
        persona_id: int,
        data: Dict
    ) -> Persona:
        """Add custom hyper-personalization data"""
        persona = persona_service.get_persona_by_id(persona_id)
        if not persona:
            raise ValueError("Persona not found")
        
        ***REMOVED*** Merge with existing hyper-personalization data
        existing_data = persona.hyper_personalization_data or {}
        merged_data = {**existing_data, **data}
        
        persona_service.update_persona(persona_id, hyper_personalization_data=merged_data)
        
        return persona_service.get_persona_by_id(persona_id)


***REMOVED*** Global instance
persona_enrichment_service = PersonaEnrichmentService()

