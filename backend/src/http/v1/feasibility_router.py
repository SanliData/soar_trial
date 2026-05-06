"""
ROUTER: feasibility_router
PURPOSE: Access feasibility preview API endpoints (aggregated counts only)
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.feasibility_service import get_feasibility_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feasibility", tags=["feasibility"])


class FeasibilityReportRequest(BaseModel):
    """Request model for generating feasibility report"""
    onboarding_plan_id: Optional[str] = Field(None, description="Onboarding plan UUID")
    geography: Optional[str] = Field(None, description="Geographic region (e.g., 'USA')")
    target_type: Optional[str] = Field(None, description="Target type (e.g., 'B2B')")
    decision_roles: Optional[str] = Field(None, description="Target roles (e.g., 'CEO, CTO')")
    region: Optional[str] = Field(None, description="Region description")


class FeasibilityReportResponse(BaseModel):
    """Response model for feasibility report (preview only, aggregated counts)"""
    id: int
    user_id: int
    onboarding_plan_id: Optional[str]
    geography: Optional[str]
    region: Optional[str]
    target_type: Optional[str]
    decision_roles: Optional[str]
    
    ***REMOVED*** Aggregated counts (NO PERSONAL DATA)
    total_businesses: int
    target_department_size: Optional[str]
    corporate_email_count: int
    phone_contact_count: int
    linkedin_profile_count: int
    ad_only_reachable_count: int
    
    ***REMOVED*** Aggregated distributions (anonymized)
    industry_distribution: Optional[dict]
    company_size_distribution: Optional[dict]
    
    ***REMOVED*** Access control
    is_unlocked: bool
    
    ***REMOVED*** Metadata
    created_at: str
    updated_at: str


class UnlockFeasibilityRequest(BaseModel):
    """Request model for unlocking feasibility report"""
    report_id: int
    purchase_id: str = Field(..., description="Purchase/subscription ID")


@router.post("/generate", response_model=FeasibilityReportResponse)
async def generate_feasibility_report(
    request: FeasibilityReportRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Generate aggregated feasibility report (preview only).
    Returns ONLY counts - no personal data or company names.
    Report is locked by default until purchase.
    """
    try:
        feasibility_service = get_feasibility_service(db)
        
        result = feasibility_service.generate_feasibility_report(
            user_id=user_id,
            onboarding_plan_id=request.onboarding_plan_id,
            geography=request.geography,
            target_type=request.target_type,
            decision_roles=request.decision_roles,
            region=request.region
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to generate feasibility report"))
        
        return FeasibilityReportResponse(**result["report"])
        
    except Exception as e:
        logger.error(f"Error generating feasibility report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating feasibility report: {str(e)}")


@router.get("/report/{report_id}", response_model=FeasibilityReportResponse)
async def get_feasibility_report(
    report_id: int,
    user_id: int = Query(..., description="User ID"),
    include_unlocked: bool = Query(False, description="Include unlocked data if access gate is open"),
    db: Session = Depends(get_db)
):
    """
    Get feasibility report (preview mode by default).
    Returns aggregated counts only - no personal data.
    Set include_unlocked=true to access unlocked data (requires purchase).
    """
    try:
        feasibility_service = get_feasibility_service(db)
        
        report = feasibility_service.get_feasibility_report(
            user_id=user_id,
            report_id=report_id,
            include_unlocked_data=include_unlocked
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="Feasibility report not found")
        
        return FeasibilityReportResponse(**report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feasibility report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting feasibility report: {str(e)}")


@router.post("/unlock")
async def unlock_feasibility_report(
    request: UnlockFeasibilityRequest,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Unlock feasibility report after purchase.
    Grants access to underlying data (still aggregated, but more detailed).
    Logs usage for billing.
    """
    try:
        feasibility_service = get_feasibility_service(db)
        
        result = feasibility_service.unlock_feasibility_report(
            user_id=user_id,
            report_id=request.report_id,
            purchase_id=request.purchase_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to unlock feasibility report"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlocking feasibility report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error unlocking feasibility report: {str(e)}")
