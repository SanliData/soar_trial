***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Personas Router - Persona havuzu API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from backend.services.b2b import persona_service, decision_maker_service, persona_enrichment_service
from backend.models.b2b_persona import Persona

router = APIRouter(prefix="/api/v1/b2b/personas", tags=["B2B"])


class PersonaCreate(BaseModel):
    company_id: int
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_profile_id: Optional[str] = None
    source_platform: str = "manual"
    profile_data: Optional[dict] = None
    ***REMOVED*** Hyper-personalization fields
    work_location_address: Optional[str] = None
    work_location_floor: Optional[str] = None
    spouse_name: Optional[str] = None
    spouse_occupation: Optional[str] = None
    children_count: Optional[int] = None
    children_info: Optional[list] = None
    interests: Optional[list] = None
    hobbies: Optional[list] = None
    education: Optional[list] = None
    alma_mater: Optional[str] = None
    certifications: Optional[list] = None
    previous_companies: Optional[list] = None
    years_of_experience: Optional[int] = None
    preferred_communication_method: Optional[str] = None
    preferred_contact_time: Optional[str] = None
    language_preferences: Optional[list] = None
    hyper_personalization_data: Optional[dict] = None


class PersonaBulkCreate(BaseModel):
    personas: List[PersonaCreate]


@router.post("/", response_model=dict)
async def create_persona(persona_data: PersonaCreate):
    """Create new persona"""
    try:
        persona = persona_service.create_persona(
            company_id=persona_data.company_id,
            full_name=persona_data.full_name,
            first_name=persona_data.first_name,
            last_name=persona_data.last_name,
            email=persona_data.email,
            phone=persona_data.phone,
            job_title=persona_data.job_title,
            department=persona_data.department,
            linkedin_url=persona_data.linkedin_url,
            linkedin_profile_id=persona_data.linkedin_profile_id,
            source_platform=persona_data.source_platform,
            profile_data=persona_data.profile_data,
            work_location_address=persona_data.work_location_address,
            work_location_floor=persona_data.work_location_floor,
            spouse_name=persona_data.spouse_name,
            spouse_occupation=persona_data.spouse_occupation,
            children_count=persona_data.children_count,
            children_info=persona_data.children_info,
            interests=persona_data.interests,
            hobbies=persona_data.hobbies,
            education=persona_data.education,
            alma_mater=persona_data.alma_mater,
            certifications=persona_data.certifications,
            previous_companies=persona_data.previous_companies,
            years_of_experience=persona_data.years_of_experience,
            preferred_communication_method=persona_data.preferred_communication_method,
            preferred_contact_time=persona_data.preferred_contact_time,
            language_preferences=persona_data.language_preferences,
            hyper_personalization_data=persona_data.hyper_personalization_data
        )
        return persona.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk", response_model=dict)
async def bulk_create_personas(bulk_data: PersonaBulkCreate):
    """Toplu persona oluştur"""
    try:
        personas_data = [p.dict() for p in bulk_data.personas]
        personas = persona_service.bulk_create_personas(personas_data)
        return {
            "created": len(personas),
            "personas": [p.to_dict() for p in personas]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def get_personas(
    company_id: Optional[int] = Query(None),
    is_decision_maker: Optional[bool] = Query(None),
    decision_maker_type: Optional[str] = Query(None)
):
    """Persona listesi"""
    try:
        if company_id:
            personas = persona_service.get_personas_by_company(company_id)
        else:
            personas = []
        
        ***REMOVED*** Filtreleme
        if is_decision_maker is not None:
            personas = [p for p in personas if p.is_decision_maker == is_decision_maker]
        if decision_maker_type:
            personas = [p for p in personas if p.decision_maker_type == decision_maker_type]
        
        return {
            "total": len(personas),
            "personas": [p.to_dict() for p in personas]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{persona_id}", response_model=dict)
async def get_persona(persona_id: int):
    """Persona detayı"""
    persona = persona_service.get_persona_by_id(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona.to_dict()


@router.put("/{persona_id}", response_model=dict)
async def update_persona(persona_id: int, persona_data: PersonaCreate):
    """Persona bilgilerini güncelle"""
    persona = persona_service.update_persona(
        persona_id,
        **persona_data.dict(exclude_unset=True)
    )
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona.to_dict()


@router.get("/decision-makers/search", response_model=dict)
async def search_decision_makers(
    company_id: Optional[int] = Query(None),
    decision_maker_type: Optional[str] = Query(None),
    min_authority: str = Query("low", regex="^(low|medium|high)$")
):
    """Karar vericileri ara"""
    try:
        decision_makers = decision_maker_service.find_decision_makers_by_type(
            company_id=company_id,
            decision_maker_type=decision_maker_type,
            min_authority=min_authority
        )
        return {
            "total": len(decision_makers),
            "decision_makers": [dm.to_dict() for dm in decision_makers]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/decision-makers", response_model=dict)
async def get_decision_maker_statistics(
    company_id: Optional[int] = Query(None)
):
    """Karar verici istatistikleri"""
    return decision_maker_service.get_decision_maker_statistics(company_id=company_id)


@router.get("/statistics/personas", response_model=dict)
async def get_persona_statistics(
    company_id: Optional[int] = Query(None)
):
    """Persona pool statistics"""
    return persona_service.get_persona_statistics(company_id=company_id)


@router.post("/{persona_id}/enrich", response_model=dict)
async def enrich_persona(persona_id: int):
    """Enrich persona with hyper-personalization data from open sources"""
    try:
        persona = persona_enrichment_service.enrich_persona_from_open_sources(persona_id)
        return persona.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{persona_id}/enrich/linkedin", response_model=dict)
async def enrich_persona_from_linkedin(persona_id: int):
    """Enrich persona from LinkedIn profile"""
    try:
        persona = persona_enrichment_service.enrich_persona_from_linkedin(persona_id)
        return persona.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{persona_id}/hyper-personalization", response_model=dict)
async def add_hyper_personalization_data(
    persona_id: int,
    data: dict
):
    """Add custom hyper-personalization data to persona"""
    try:
        persona = persona_enrichment_service.add_hyper_personalization_data(persona_id, data)
        return persona.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

