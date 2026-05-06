"""
ROUTER: sales_page_audit_router
PURPOSE: API endpoints for sales page audit
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any

from src.services.sales_page_audit_service import get_sales_page_audit_service
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.middleware.locale_middleware import get_locale_from_request
from src.db.base import get_db
from src.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sales-page-audit", tags=["sales-page-audit"])


# Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class SalesPageAuditRequest(BaseModel):
    """Request model for sales page audit."""
    url: HttpUrl
    target_market: str = "US"
    business_type: Optional[str] = None


class SalesPageAuditResponse(BaseModel):
    """Response model for sales page audit."""
    success: bool
    url: str
    target_market: str
    audit: Optional[Dict[str, Any]] = None
    raw_analysis: Optional[str] = None
    error: Optional[str] = None


@router.post("/audit", response_model=SalesPageAuditResponse)
async def audit_sales_page(
    request: SalesPageAuditRequest,
    http_request: Request,
    user: Optional[User] = Depends(get_current_user_from_header)
):
    """
    Audit a sales page and provide optimization recommendations.
    
    Uses Gemini AI to analyze the page for US market optimization (LPO).
    """
    try:
        # Get locale from request
        locale = get_locale_from_request(http_request)
        
        audit_service = get_sales_page_audit_service()
        
        result = audit_service.audit_sales_page(
            url=str(request.url),
            target_market=request.target_market,
            business_type=request.business_type,
            locale=locale
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Audit failed")
            )
        
        return SalesPageAuditResponse(
            success=True,
            url=result.get("url"),
            target_market=result.get("target_market"),
            audit=result.get("audit"),
            raw_analysis=result.get("raw_analysis")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error auditing sales page: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "sales-page-audit"}

