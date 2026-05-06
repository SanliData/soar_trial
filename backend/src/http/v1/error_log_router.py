"""
ROUTER: error_log_router
PURPOSE: Error log endpoints for debugging and monitoring
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.error_logging_service import get_error_logging_service

router = APIRouter(prefix="/error-logs", tags=["error-logs"])


***REMOVED*** Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class ErrorLogListResponse(BaseModel):
    success: bool
    error_logs: List[Dict[str, Any]]
    total: int


@router.get("/list", response_model=ErrorLogListResponse)
async def get_error_logs(
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    unresolved_only: bool = Query(False, description="Only unresolved errors"),
    limit: int = Query(100, description="Maximum number of logs"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get error logs with filters.
    Requires authentication.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        error_service = get_error_logging_service(db)
        error_logs = error_service.get_error_logs(
            service_name=service_name,
            severity=severity,
            unresolved_only=unresolved_only,
            user_id=user.id,
            limit=limit
        )
        
        return ErrorLogListResponse(
            success=True,
            error_logs=error_logs,
            total=len(error_logs)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting error logs: {str(e)}")


@router.get("/statistics")
async def get_error_statistics(
    days: int = Query(7, description="Number of days to analyze"),
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get error statistics for the last N days.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        error_service = get_error_logging_service(db)
        statistics = error_service.get_error_statistics(days=days)
        
        return statistics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting error statistics: {str(e)}")


@router.post("/{error_log_id}/resolve")
async def mark_error_resolved(
    error_log_id: int,
    resolution_notes: Optional[str] = None,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Mark an error as resolved.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        error_service = get_error_logging_service(db)
        result = error_service.mark_error_resolved(
            error_log_id=error_log_id,
            resolution_notes=resolution_notes
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Error log not found"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking error as resolved: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "error-logs"
    }


