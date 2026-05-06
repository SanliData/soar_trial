"""
ROUTER: usage_billing_router
PURPOSE: Usage-based billing API endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.usage_billing_service import UsageBillingService
from src.services.trial_service import TrialService
from src.services.ad_spend_comparison_service import AdSpendComparisonService

router = APIRouter(prefix="/usage-billing", tags=["usage-billing"])


***REMOVED*** Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


***REMOVED*** Dependency injection
def get_usage_billing_service(db: Session = Depends(get_db)) -> UsageBillingService:
    """Get usage billing service instance"""
    return UsageBillingService(db)


def get_trial_service(db: Session = Depends(get_db)) -> TrialService:
    """Get trial service instance"""
    return TrialService(db)


def get_ad_spend_comparison_service(db: Session = Depends(get_db)) -> AdSpendComparisonService:
    """Get ad spend comparison service instance"""
    return AdSpendComparisonService(db)


***REMOVED*** Request models
class RecordUsageEventRequest(BaseModel):
    event_type: str
    quantity: int = 1
    metadata: Optional[Dict[str, Any]] = None
    company_id: Optional[int] = None
    persona_id: Optional[int] = None
    campaign_id: Optional[int] = None


class AdSpendComparisonRequest(BaseModel):
    billing_period: Optional[str] = None
    industry: str = "b2b"
    region: str = "US"


***REMOVED*** Endpoints
@router.get("/pricing")
async def get_pricing_info(
    billing_service: UsageBillingService = Depends(get_usage_billing_service)
):
    """
    Get pricing information for all operations.
    Public endpoint - no authentication required.
    """
    try:
        return billing_service.get_pricing_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pricing info: {str(e)}")


@router.post("/events")
async def record_usage_event(
    event_data: RecordUsageEventRequest,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    billing_service: UsageBillingService = Depends(get_usage_billing_service)
):
    """
    Record a usage event for billing.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = billing_service.record_usage_event(
            user_id=user.id,
            event_type=event_data.event_type,
            quantity=event_data.quantity,
            metadata=event_data.metadata,
            company_id=event_data.company_id,
            persona_id=event_data.persona_id,
            campaign_id=event_data.campaign_id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to record event"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording usage event: {str(e)}")


@router.get("/usage")
async def get_usage_summary(
    billing_period: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    billing_service: UsageBillingService = Depends(get_usage_billing_service)
):
    """
    Get usage summary for current or specified billing period.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = billing_service.get_period_usage(
            user_id=user.id,
            billing_period=billing_period
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to get usage"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage: {str(e)}")


@router.get("/trial/status")
async def get_trial_status(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    trial_service: TrialService = Depends(get_trial_service)
):
    """
    Get trial status for current user.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return trial_service.get_trial_status(user.id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting trial status: {str(e)}")


@router.post("/trial/start")
async def start_trial(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    trial_service: TrialService = Depends(get_trial_service)
):
    """
    Start a 30-day free trial.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = trial_service.start_trial(user.id)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to start trial"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting trial: {str(e)}")


@router.post("/ad-spend-comparison")
async def get_ad_spend_comparison(
    comparison_data: AdSpendComparisonRequest,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db),
    comparison_service: AdSpendComparisonService = Depends(get_ad_spend_comparison_service)
):
    """
    Get comparison between SOAR spend and estimated traditional ad spend.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        result = comparison_service.estimate_traditional_ad_spend(
            user_id=user.id,
            billing_period=comparison_data.billing_period,
            industry=comparison_data.industry,
            region=comparison_data.region
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to get comparison"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting ad spend comparison: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "usage-billing"
    }
