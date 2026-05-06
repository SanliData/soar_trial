"""
SERVICE: usage_tracking_service
PURPOSE: Service for tracking user usage against plan limits
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.usage_tracking import UsageTracking
from src.models.company import Company
from src.models.persona import Persona
from src.models.campaign import Campaign
from src.models.appointment import Appointment
from src.models.lead import Lead
from src.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class UsageTrackingService:
    """
    Service for tracking user usage and enforcing plan limits.
    """
    
    def __init__(self, db: Session):
        """Initialize Usage Tracking Service with database session."""
        self.db = db
        self.payment_service = PaymentService(db)
    
    def get_current_period(self) -> str:
        """
        Get current period string (YYYY-MM format).
        
        Returns:
            Current period string
        """
        now = datetime.utcnow()
        return now.strftime("%Y-%m")
    
    def get_or_create_usage_tracking(
        self,
        user_id: int,
        period: Optional[str] = None
    ) -> UsageTracking:
        """
        Get or create usage tracking for a user and period.
        
        Args:
            user_id: User ID
            period: Period string (YYYY-MM). If None, uses current period.
        
        Returns:
            UsageTracking object
        """
        if period is None:
            period = self.get_current_period()
        
        usage = self.db.query(UsageTracking).filter(
            UsageTracking.user_id == user_id,
            UsageTracking.period == period
        ).first()
        
        if not usage:
            usage = UsageTracking(
                user_id=user_id,
                period=period
            )
            self.db.add(usage)
            self.db.commit()
            self.db.refresh(usage)
        
        return usage
    
    def increment_usage(
        self,
        user_id: int,
        usage_type: str,
        amount: int = 1,
        conversion_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Increment usage counter for a user.
        
        Args:
            user_id: User ID
            usage_type: Type of usage ("companies", "personas", "campaigns", "appointments", "leads", "conversions")
            amount: Amount to increment (default: 1)
            conversion_type: Conversion type for tracking ("appointment", "direct_traffic")
        
        Returns:
            Dictionary with result
        """
        try:
            period = self.get_current_period()
            usage = self.get_or_create_usage_tracking(user_id, period)
            
            if usage_type == "companies":
                usage.companies_count += amount
            elif usage_type == "personas":
                usage.personas_count += amount
            elif usage_type == "campaigns":
                usage.campaigns_count += amount
            elif usage_type == "appointments":
                usage.appointments_count += amount
            elif usage_type == "leads":
                usage.leads_count += amount
            elif usage_type == "conversions":
                ***REMOVED*** Track conversions by type
                if conversion_type == "appointment":
                    usage.appointments_count += amount
                elif conversion_type == "direct_traffic":
                    ***REMOVED*** Direct traffic conversions are tracked separately
                    ***REMOVED*** We can add a new field later if needed
                    usage.leads_count += amount  ***REMOVED*** Track as leads for now
                else:
                    usage.leads_count += amount
            else:
                return {
                    "success": False,
                    "error": f"Invalid usage type: {usage_type}"
                }
            
            self.db.commit()
            self.db.refresh(usage)
            
            return {
                "success": True,
                "usage": usage.to_dict()
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing usage: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def get_usage_statistics(
        self,
        user_id: int,
        period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a user.
        
        Args:
            user_id: User ID
            period: Period string (YYYY-MM). If None, uses current period.
        
        Returns:
            Dictionary with usage statistics and plan limits
        """
        try:
            if period is None:
                period = self.get_current_period()
            
            usage = self.get_or_create_usage_tracking(user_id, period)
            
            ***REMOVED*** Get user's subscription
            subscription = self.payment_service.get_user_subscription(user_id)
            plan_type = subscription.get("plan_type", "free") if subscription else "free"
            plan = self.payment_service.PLANS.get(plan_type, self.payment_service.PLANS["free"])
            limits = plan.get("limits", {})
            
            ***REMOVED*** Calculate usage percentages
            companies_limit = limits.get("companies_per_month", 0)
            personas_limit = limits.get("personas_per_month", 0)
            campaigns_limit = limits.get("campaigns_per_month", 0)
            
            companies_percentage = (
                (usage.companies_count / companies_limit * 100) if companies_limit > 0 else 0
            ) if companies_limit != -1 else 0  ***REMOVED*** -1 means unlimited
            
            personas_percentage = (
                (usage.personas_count / personas_limit * 100) if personas_limit > 0 else 0
            ) if personas_limit != -1 else 0
            
            campaigns_percentage = (
                (usage.campaigns_count / campaigns_limit * 100) if campaigns_limit > 0 else 0
            ) if campaigns_limit != -1 else 0
            
            return {
                "success": True,
                "period": period,
                "plan_type": plan_type,
                "usage": {
                    "companies": {
                        "count": usage.companies_count,
                        "limit": companies_limit if companies_limit != -1 else None,
                        "percentage": min(companies_percentage, 100),
                        "unlimited": companies_limit == -1
                    },
                    "personas": {
                        "count": usage.personas_count,
                        "limit": personas_limit if personas_limit != -1 else None,
                        "percentage": min(personas_percentage, 100),
                        "unlimited": personas_limit == -1
                    },
                    "campaigns": {
                        "count": usage.campaigns_count,
                        "limit": campaigns_limit if campaigns_limit != -1 else None,
                        "percentage": min(campaigns_percentage, 100),
                        "unlimited": campaigns_limit == -1
                    },
                    "appointments": {
                        "count": usage.appointments_count,
                        "limit": None,  ***REMOVED*** Appointments are typically unlimited
                        "unlimited": True
                    },
                    "leads": {
                        "count": usage.leads_count,
                        "limit": None,  ***REMOVED*** Leads are typically unlimited
                        "unlimited": True
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting usage statistics: {str(e)}")
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }
    
    def check_limit(
        self,
        user_id: int,
        usage_type: str
    ) -> Dict[str, Any]:
        """
        Check if user can perform an action based on plan limits.
        
        Args:
            user_id: User ID
            usage_type: Type of usage to check ("companies", "personas", "campaigns")
        
        Returns:
            Dictionary with allowed status and remaining count
        """
        try:
            stats = self.get_usage_statistics(user_id)
            
            if not stats.get("success"):
                return {
                    "allowed": False,
                    "error": stats.get("error", "Failed to check limits")
                }
            
            usage_data = stats["usage"].get(usage_type)
            if not usage_data:
                return {
                    "allowed": False,
                    "error": f"Invalid usage type: {usage_type}"
                }
            
            ***REMOVED*** If unlimited, always allowed
            if usage_data.get("unlimited"):
                return {
                    "allowed": True,
                    "remaining": None,
                    "unlimited": True
                }
            
            ***REMOVED*** Check if limit reached
            count = usage_data["count"]
            limit = usage_data["limit"]
            
            if limit is None or count < limit:
                remaining = (limit - count) if limit else None
                return {
                    "allowed": True,
                    "remaining": remaining,
                    "unlimited": False
                }
            else:
                return {
                    "allowed": False,
                    "remaining": 0,
                    "unlimited": False,
                    "error": f"{usage_type.capitalize()} limit reached. Upgrade your plan to continue."
                }
            
        except Exception as e:
            logger.error(f"Error checking limit: {str(e)}")
            return {
                "allowed": False,
                "error": f"Error: {str(e)}"
            }


def get_usage_tracking_service(db: Session) -> UsageTrackingService:
    """
    Get UsageTrackingService instance with database session.
    """
    return UsageTrackingService(db)

