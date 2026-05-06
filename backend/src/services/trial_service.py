"""
SERVICE: trial_service
PURPOSE: Manage 30-day free trial with limits
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.models.subscription import Subscription
from src.models.usage_tracking import UsageTracking

logger = logging.getLogger(__name__)


class TrialService:
    """
    Service for managing 30-day free trial with usage limits.
    """
    
    ***REMOVED*** Trial limits
    TRIAL_LIMITS = {
        "max_companies": 100,
        "max_personas": 25,
        "light_enrichment_only": True,
        "no_direct_outreach": True,
        "no_real_ad_spend": True,
    }
    
    TRIAL_DURATION_DAYS = 30
    
    def __init__(self, db: Session):
        """Initialize Trial Service with database session."""
        self.db = db
    
    def is_trial_active(self, subscription: Subscription) -> bool:
        """
        Check if trial is currently active.
        
        Args:
            subscription: Subscription object
        
        Returns:
            True if trial is active, False otherwise
        """
        if not subscription.trial_end:
            return False
        
        now = datetime.utcnow()
        if subscription.trial_started_at:
            ***REMOVED*** Check if trial has started
            if now < subscription.trial_started_at:
                return False
        
        ***REMOVED*** Check if trial has ended
        return now < subscription.trial_end
    
    def start_trial(self, user_id: int) -> Dict[str, Any]:
        """
        Start a 30-day trial for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with result
        """
        try:
            ***REMOVED*** Get or create subscription
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if not subscription:
                ***REMOVED*** Create new subscription with trial
                subscription = Subscription(
                    user_id=user_id,
                    plan_type="usage_based",
                    billing_mode="usage_based",
                    status="active",
                    trial_started_at=datetime.utcnow(),
                    trial_end=datetime.utcnow() + timedelta(days=self.TRIAL_DURATION_DAYS),
                    base_subscription_price=0.0  ***REMOVED*** Free during trial
                )
                self.db.add(subscription)
            else:
                ***REMOVED*** Update existing subscription to start trial
                if subscription.trial_end and datetime.utcnow() < subscription.trial_end:
                    return {
                        "success": False,
                        "error": "Trial already active"
                    }
                subscription.plan_type = "usage_based"
                subscription.billing_mode = "usage_based"
                subscription.trial_started_at = datetime.utcnow()
                subscription.trial_end = datetime.utcnow() + timedelta(days=self.TRIAL_DURATION_DAYS)
                subscription.base_subscription_price = 0.0
            
            self.db.commit()
            self.db.refresh(subscription)
            
            logger.info(f"Trial started for user_id={user_id}, trial_end={subscription.trial_end}")
            
            return {
                "success": True,
                "trial_started_at": subscription.trial_started_at.isoformat(),
                "trial_end": subscription.trial_end.isoformat(),
                "limits": self.TRIAL_LIMITS
            }
            
        except Exception as e:
            logger.error(f"Error starting trial: {e}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_trial_limit(
        self,
        user_id: int,
        limit_type: str,
        current_count: int
    ) -> Dict[str, Any]:
        """
        Check if user has exceeded trial limit.
        
        Args:
            user_id: User ID
            limit_type: Type of limit (companies, personas, etc.)
            current_count: Current count
        
        Returns:
            Dictionary with limit check result
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if not subscription or not self.is_trial_active(subscription):
                ***REMOVED*** Not in trial, no limits
                return {
                    "success": True,
                    "in_trial": False,
                    "limit_exceeded": False,
                    "limit": None,
                    "current": current_count
                }
            
            ***REMOVED*** Check limits
            limit_map = {
                "companies": self.TRIAL_LIMITS["max_companies"],
                "personas": self.TRIAL_LIMITS["max_personas"],
            }
            
            limit = limit_map.get(limit_type)
            if limit is None:
                return {
                    "success": True,
                    "in_trial": True,
                    "limit_exceeded": False,
                    "limit": None,
                    "current": current_count
                }
            
            limit_exceeded = current_count >= limit
            
            return {
                "success": True,
                "in_trial": True,
                "limit_exceeded": limit_exceeded,
                "limit": limit,
                "current": current_count,
                "remaining": max(0, limit - current_count)
            }
            
        except Exception as e:
            logger.error(f"Error checking trial limit: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_trial_status(self, user_id: int) -> Dict[str, Any]:
        """
        Get trial status for a user.
        
        Args:
            user_id: User ID
        
        Returns:
            Dictionary with trial status
        """
        try:
            subscription = self.db.query(Subscription).filter(
                Subscription.user_id == user_id
            ).first()
            
            if not subscription:
                return {
                    "success": True,
                    "in_trial": False,
                    "trial_active": False
                }
            
            trial_active = self.is_trial_active(subscription)
            
            result = {
                "success": True,
                "in_trial": trial_active,
                "trial_active": trial_active,
                "limits": self.TRIAL_LIMITS if trial_active else None
            }
            
            if subscription.trial_started_at:
                result["trial_started_at"] = subscription.trial_started_at.isoformat()
            
            if subscription.trial_end:
                result["trial_end"] = subscription.trial_end.isoformat()
                if trial_active:
                    now = datetime.utcnow()
                    remaining = (subscription.trial_end - now).days
                    result["days_remaining"] = max(0, remaining)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting trial status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
