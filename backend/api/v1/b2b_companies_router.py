***REMOVED*** -*- coding: utf-8 -*-
"""
B2B Companies Router - Müşteri havuzu API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from backend.services.b2b import customer_pool_service, address_validation_service
from backend.models.b2b_company import Company

router = APIRouter(prefix="/api/v1/b2b/companies", tags=["B2B"])


class CompanyCreate(BaseModel):
    name: str
    official_name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    metadata: Optional[dict] = None


class CompanyBulkCreate(BaseModel):
    companies: List[CompanyCreate]


@router.post("/", response_model=dict)
async def create_company(company_data: CompanyCreate):
    """Yeni şirket oluştur"""
    try:
        company = customer_pool_service.create_company(
            name=company_data.name,
            official_name=company_data.official_name,
            website=company_data.website,
            industry=company_data.industry,
            company_size=company_data.company_size,
            address_line1=company_data.address_line1,
            address_line2=company_data.address_line2,
            city=company_data.city,
            state=company_data.state,
            postal_code=company_data.postal_code,
            country=company_data.country,
            metadata=company_data.metadata
        )
        return company.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk", response_model=dict)
async def bulk_create_companies(bulk_data: CompanyBulkCreate):
    """Toplu şirket oluştur"""
    try:
        companies_data = [c.dict() for c in bulk_data.companies]
        companies = customer_pool_service.bulk_create_companies(companies_data)
        return {
            "created": len(companies),
            "companies": [c.to_dict() for c in companies]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def search_companies(
    name: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Şirket arama"""
    try:
        companies = customer_pool_service.search_companies(
            name=name,
            industry=industry,
            city=city,
            country=country,
            limit=limit,
            offset=offset
        )
        return {
            "total": len(companies),
            "companies": [c.to_dict() for c in companies]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{company_id}", response_model=dict)
async def get_company(company_id: int):
    """Şirket detayı"""
    company = customer_pool_service.get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.to_dict()


@router.put("/{company_id}", response_model=dict)
async def update_company(company_id: int, company_data: CompanyCreate):
    """Şirket bilgilerini güncelle"""
    company = customer_pool_service.update_company(
        company_id,
        **company_data.dict(exclude_unset=True)
    )
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.to_dict()


@router.post("/{company_id}/validate-address", response_model=dict)
async def validate_company_address(company_id: int):
    """Şirket adresini doğrula"""
    company = customer_pool_service.get_company_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    success = address_validation_service.validate_company_address(company)
    return {
        "company_id": company_id,
        "validated": success,
        "latitude": company.latitude if success else None,
        "longitude": company.longitude if success else None
    }


@router.post("/validate-addresses/batch", response_model=dict)
async def batch_validate_addresses(
    company_ids: Optional[List[int]] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Toplu adres doğrulama"""
    try:
        result = address_validation_service.batch_validate_addresses(
            company_ids=company_ids,
            limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics/pool", response_model=dict)
async def get_pool_statistics():
    """Müşteri havuzu istatistikleri"""
    return customer_pool_service.get_pool_statistics()

