"""
ROUTER: sniper_b2b_router
PURPOSE: API endpoints for Sniper-B2B Autonomous Sales Cycle
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.services.sniper_b2b_service import get_sniper_b2b_service
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.middleware.locale_middleware import get_locale_from_request
from src.models.company import Company
from src.models.user import User
from src.db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sniper-b2b", tags=["sniper-b2b"])


***REMOVED*** Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class SniperCycleRequest(BaseModel):
    """Request model for Sniper cycle execution."""
    raw_material: str


class SniperCampaignRequest(BaseModel):
    """Request model for creating sniper campaign."""
    producer_id: int
    customer_id: str
    raw_material: str


class MarkWonRequest(BaseModel):
    """Request model for marking company as won."""
    company_id: int
    conversion_type: str  ***REMOVED*** "lead_form", "appointment", "sale"


@router.post("/execute-cycle", response_model=None)
async def execute_sniper_cycle(
    request: SniperCycleRequest,
    http_request: Request,
    user: Optional[User] = Depends(get_current_user_from_header)
):
    """
    Execute complete Sniper-B2B cycle: X -> Y -> Producers -> Geocode -> Personas -> Ads.
    
    Returns all enriched producer data with coordinates, personas, and ad copies.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        locale = get_locale_from_request(http_request)
        
        sniper_service = get_sniper_b2b_service()
        
        result = sniper_service.execute_sniper_cycle(
            raw_material=request.raw_material,
            user_id=user.id,
            locale=locale
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Sniper cycle failed")
            )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing sniper cycle: {str(e)}"
        )


@router.post("/create-campaign", response_model=None)
async def create_sniper_campaign(
    request: SniperCampaignRequest,
    http_request: Request,
    user: Optional[User] = Depends(get_current_user_from_header)
):
    """
    Create a Google Ads campaign with 10m radius targeting for a producer.
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        locale = get_locale_from_request(http_request)
        
        ***REMOVED*** Get producer data (would be from database or cache)
        ***REMOVED*** For now, this is a placeholder - producer data should be stored after execute-cycle
        
        sniper_service = get_sniper_b2b_service()
        
        ***REMOVED*** This would get producer from database
        producer = {
            "id": request.producer_id,
            "sniper_ready": True,
            "coordinates": {
                "latitude": 0.0,  ***REMOVED*** Would be from database
                "longitude": 0.0
            }
        }
        
        result = sniper_service.create_sniper_campaign(
            producer=producer,
            customer_id=request.customer_id,
            user_id=user.id,
            raw_material=request.raw_material,
            locale=locale
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating sniper campaign: {str(e)}"
        )


@router.post("/mark-won", response_model=None)
async def mark_company_won(
    request: MarkWonRequest,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Mark a company as "Won Customer" after successful conversion.
    
    This is called when:
    - Lead form is filled (Step 11)
    - Appointment is booked (Step 11)
    - Direct sale is completed
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        company = db.query(Company).filter(
            Company.id == request.company_id,
            Company.user_id == user.id
        ).first()
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
        
        ***REMOVED*** Update company status
        company.status = "won"
        company.cycle_status = "won"
        
        ***REMOVED*** Update metadata
        if not company.company_metadata:
            company.company_metadata = {}
        
        company.company_metadata["won_date"] = None  ***REMOVED*** Would be datetime.utcnow().isoformat()
        company.company_metadata["conversion_type"] = request.conversion_type
        
        db.commit()
        db.refresh(company)
        
        return {
            "success": True,
            "message": f"Company {company.name} marked as won customer",
            "company": company.to_dict()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error marking company as won: {str(e)}"
        )


@router.get("/won-customers", response_model=None)
async def get_won_customers(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get list of won customers (companies with status='won').
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        won_companies = db.query(Company).filter(
            Company.user_id == user.id,
            Company.status == "won"
        ).all()
        
        return {
            "success": True,
            "total": len(won_companies),
            "companies": [company.to_dict() for company in won_companies]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching won customers: {str(e)}"
        )


@router.get("/health", response_model=None)
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "sniper-b2b"}

