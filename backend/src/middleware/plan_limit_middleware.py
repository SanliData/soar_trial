"""
MIDDLEWARE: plan_limit_middleware
PURPOSE: Middleware to enforce subscription plan limits
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Callable
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.services.usage_tracking_service import get_usage_tracking_service
from src.services.auth_service import get_current_user_dependency, is_admin_email

logger = logging.getLogger(__name__)


def check_plan_limit(usage_type: str):
    """
    Dependency function to check plan limits before allowing an action.
    
    Args:
        usage_type: Type of usage to check ("companies", "personas", "campaigns")
    
    Returns:
        Dependency function
    """
    async def limit_checker(
        request: Request,
        authorization: str = None,
        db: Session = Depends(get_db)
    ):
        ***REMOVED*** Get current user
        if not authorization:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        try:
            user = get_current_user_dependency(authorization=authorization, db=db)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        ***REMOVED*** Admin users (e.g. isanli058@gmail.com) bypass plan/payment limits
        if is_admin_email(getattr(user, "email", None)):
            return user

        ***REMOVED*** Check plan limit
        usage_service = get_usage_tracking_service(db)
        limit_check = usage_service.check_limit(user.id, usage_type)
        
        if not limit_check.get("allowed"):
            error_msg = limit_check.get("error", "Plan limit reached")
            raise HTTPException(
                status_code=403,
                detail={
                    "error": error_msg,
                    "usage_type": usage_type,
                    "remaining": limit_check.get("remaining"),
                    "unlimited": limit_check.get("unlimited", False)
                }
            )
        
        return user
    
    return limit_checker


***REMOVED*** Convenience functions for common usage types
def check_companies_limit():
    """Check companies limit."""
    return check_plan_limit("companies")


def check_personas_limit():
    """Check personas limit."""
    return check_plan_limit("personas")


def check_campaigns_limit():
    """Check campaigns limit."""
    return check_plan_limit("campaigns")


