"""
ROUTER: usage_router
PURPOSE: Usage tracking and statistics endpoints
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.usage_tracking_service import get_usage_tracking_service

router = APIRouter(prefix="/usage", tags=["usage"])


# Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class UsageStatisticsResponse(BaseModel):
    success: bool
    period: str
    plan_type: str
    usage: Dict[str, Any]


@router.get("/statistics", response_model=UsageStatisticsResponse)
async def get_usage_statistics(
    period: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for the authenticated user.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        usage_service = get_usage_tracking_service(db)
        stats = usage_service.get_usage_statistics(user.id, period)
        
        if not stats.get("success"):
            raise HTTPException(status_code=500, detail=stats.get("error", "Failed to get usage statistics"))
        
        return UsageStatisticsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting usage statistics: {str(e)}")


@router.get("/check-limit")
async def check_limit(
    usage_type: str,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Check if user can perform an action based on plan limits.
    
    Args:
        usage_type: Type of usage to check ("companies", "personas", "campaigns")
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        usage_service = get_usage_tracking_service(db)
        limit_check = usage_service.check_limit(user.id, usage_type)
        
        return limit_check
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking limit: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "usage"
    }


