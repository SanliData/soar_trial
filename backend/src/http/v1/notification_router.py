"""
ROUTER: notification_router
PURPOSE: Notification endpoints for user notifications
ENCODING: UTF-8 WITHOUT BOM
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from src.models.user import User
from src.db.base import get_db
from src.services.auth_service import get_current_user_dependency, get_current_user_impl
from src.services.notification_service import get_notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Helper function to get current user
def get_current_user_from_header(
    authorization: str = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """Helper to inject authorization header into get_current_user_dependency"""
    if authorization:
        return get_current_user_impl(authorization=authorization, db=db)
    return None


class NotificationListResponse(BaseModel):
    success: bool
    notifications: List[Dict[str, Any]]
    total: int
    unread_count: int


@router.get("/list", response_model=NotificationListResponse)
async def get_notifications(
    unread_only: bool = False,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the authenticated user.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        notification_service = get_notification_service(db)
        notifications = notification_service.get_user_notifications(
            user_id=user.id,
            unread_only=unread_only,
            limit=100
        )
        
        # Count unread notifications
        unread_notifications = notification_service.get_user_notifications(
            user_id=user.id,
            unread_only=True,
            limit=1000
        )
        
        return NotificationListResponse(
            success=True,
            notifications=notifications,
            total=len(notifications),
            unread_count=len(unread_notifications)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notifications: {str(e)}")


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Mark a notification as read.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        notification_service = get_notification_service(db)
        result = notification_service.mark_notification_read(
            notification_id=notification_id,
            user_id=user.id
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Notification not found"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")


@router.get("/unread-count")
async def get_unread_count(
    user: Optional[User] = Depends(get_current_user_from_header),
    db: Session = Depends(get_db)
):
    """
    Get count of unread notifications.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        notification_service = get_notification_service(db)
        unread_notifications = notification_service.get_user_notifications(
            user_id=user.id,
            unread_only=True,
            limit=1000
        )
        
        return {
            "success": True,
            "unread_count": len(unread_notifications)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")


@router.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "domain": "notifications"
    }


