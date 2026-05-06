"""
ROUTER: discovery_router
PURPOSE: Discovery records endpoints (protected routes example)
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.user import User
from src.models.discovery_record import DiscoveryRecord
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.usage_tracking_service import get_usage_tracking_service
from src.middleware.plan_limit_middleware import check_companies_limit

router = APIRouter(prefix="/discovery", tags=["discovery"])


# Helper function to create dependency with proper header injection
def get_current_user_from_header(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    return get_current_user_impl(authorization=authorization, db=db)


class DiscoveryRecord(BaseModel):
    id: Optional[str] = None
    company_name: str
    address: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    technology_stack: Optional[List[str]] = None
    business_activity: Optional[str] = None


class DiscoveryListResponse(BaseModel):
    success: bool
    records: List[dict]
    total: int
    user_id: int


@router.get("/records", response_model=DiscoveryListResponse)
async def get_discovery_records(
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get discovery records for the authenticated user.
    This is a protected route - requires valid JWT token.
    """
    # Get user's discovery records from database
    records = db.query(DiscoveryRecord).filter(DiscoveryRecord.user_id == user.id).all()
    
    return DiscoveryListResponse(
        success=True,
        records=[record.to_dict() for record in records],
        total=len(records),
        user_id=user.id
    )


@router.post("/records")
async def create_discovery_record(
    record: DiscoveryRecord,
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Create a new discovery record for the authenticated user.
    This is a protected route - requires valid JWT token.
    """
    # Create discovery record with user_id
    db_record = DiscoveryRecord(
        user_id=user.id,
        company_name=record.company_name,
        address=record.address,
        website=record.website,
        phone=record.phone,
        email=record.email,
        source=record.source,
        status=record.status,
        industry=record.industry,
        employee_count=record.employee_count,
        technology_stack=record.technology_stack,
        business_activity=record.business_activity
    )
    
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    # Increment usage tracking for companies
    try:
        usage_service = get_usage_tracking_service(db)
        usage_service.increment_usage(user.id, "companies", 1)
    except Exception as e:
        # Log error but don't fail the request
        import logging
        logging.error(f"Failed to increment usage tracking: {str(e)}")
    
    return {
        "success": True,
        "message": "Discovery record created",
        "record": db_record.to_dict(),
        "user_id": user.id
    }


@router.get("/records/{record_id}")
async def get_discovery_record(
    record_id: str,
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get a specific discovery record by ID.
    This is a protected route - requires valid JWT token.
    Only returns records belonging to the authenticated user.
    """
    record = db.query(DiscoveryRecord).filter(
        DiscoveryRecord.id == int(record_id),
        DiscoveryRecord.user_id == user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "success": True,
        "record": record.to_dict()
    }


@router.delete("/records/{record_id}")
async def delete_discovery_record(
    record_id: str,
    user: User = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Delete a discovery record.
    This is a protected route - requires valid JWT token.
    Only allows deletion of records belonging to the authenticated user.
    """
    record = db.query(DiscoveryRecord).filter(
        DiscoveryRecord.id == int(record_id),
        DiscoveryRecord.user_id == user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(record)
    db.commit()
    
    return {
        "success": True,
        "message": f"Record {record_id} deleted",
        "user_id": user.id
    }


@router.get("/health")
def health():
    """Public health check endpoint (not protected)."""
    return {
        "status": "ok",
        "domain": "discovery",
        "protected_routes": [
            "GET /v1/discovery/records",
            "POST /v1/discovery/records",
            "GET /v1/discovery/records/{record_id}",
            "DELETE /v1/discovery/records/{record_id}"
        ]
    }

