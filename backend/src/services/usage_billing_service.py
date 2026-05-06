"""
SERVICE: usage_billing_service
PURPOSE: AWS-style usage-based billing service
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.usage_billing_event import UsageBillingEvent
from src.models.subscription import Subscription

logger = logging.getLogger(__name__)


class UsageBillingService:
    """
    Service for managing usage-based billing (AWS-style pay-as-you-go).
    """
    
    ***REMOVED*** Pricing per operation (in USD)
    PRICING = {
        "verified_company": 0.05,  ***REMOVED*** $0.05 per verified company
        "decision_maker_match": 0.10,  ***REMOVED*** $0.10 per decision maker match
        "persona_enrichment": 0.15,  ***REMOVED*** $0.15 per persona enrichment
        "location_exposure": 0.02,  ***REMOVED*** $0.02 per location exposure
        "outreach_attempt": 0.25,  ***REMOVED*** $0.25 per outreach attempt
        "booked_meeting": 2.00,  ***REMOVED*** $2.00 per booked meeting (success-based)
    }
    
    ***REMOVED*** Base subscription fee
    BASE_SUBSCRIPTION_PRICE = 0.98  ***REMOVED*** $0.98/month
    
    def __init__(self, db: Session):
        """Initialize Usage Billing Service with database session."""
        self.db = db
    
    def get_current_billing_period(self) -> str:
        """
        Get current billing period string (YYYY-MM format).
        
        Returns:
            Current billing period string
        """
        now = datetime.utcnow()
        return now.strftime("%Y-%m")
    
    def record_usage_event(
        self,
        user_id: int,
        event_type: str,
        quantity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        company_id: Optional[int] = None,
        persona_id: Optional[int] = None,
        campaign_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record a usage event for billing.
        
        Args:
            user_id: User ID
            event_type: Type of event (verified_company, decision_maker_match, etc.)
            quantity: Quantity (usually 1)
            metadata: Additional metadata
            company_id: Related company ID (optional)
            persona_id: Related persona ID (optional)
            campaign_id: Related campaign ID (optional)
        
        Returns:
            Dictionary with result
        """
        try:
            if event_type not in self.PRICING:
                return {
                    "success": False,
                    "error": f"Unknown event type: {event_type}"
                }
            
            unit_price = self.PRICING[event_type]
            total_cost = unit_price * quantity
            billing_period = self.get_current_billing_period()
            
            ***REMOVED*** Create usage event
            event = UsageBillingEvent(
                user_id=user_id,
                event_type=event_type,
                billing_period=billing_period,
                unit_price=unit_price,
                quantity=quantity,
                total_cost=total_cost,
                currency="USD",
                event_metadata=metadata or {},
                company_id=company_id,
                persona_id=persona_id,
                campaign_id=campaign_id
            )
            
            self.db.add(event)
            self.db.commit()
            self.db.refresh(event)
            
            logger.info(f"Usage event recorded: user_id={user_id}, event_type={event_type}, cost=${total_cost}")
            
            return {
                "success": True,
                "event_id": event.id,
                "event_type": event_type,
                "cost": total_cost,
                "billing_period": billing_period
            }
            
        except Exception as e:
            logger.error(f"Error recording usage event: {e}", exc_info=True)
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_period_usage(
        self,
        user_id: int,
        billing_period: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get usage summary for a billing period.
        
        Args:
            user_id: User ID
            billing_period: Billing period (YYYY-MM). If None, uses current period.
        
        Returns:
            Dictionary with usage summary
        """
        try:
            if billing_period is None:
                billing_period = self.get_current_billing_period()
            
            ***REMOVED*** Get all events for period
            events = self.db.query(UsageBillingEvent).filter(
                and_(
                    UsageBillingEvent.user_id == user_id,
                    UsageBillingEvent.billing_period == billing_period
                )
            ).all()
            
            ***REMOVED*** Calculate totals by event type
            totals_by_type = {}
            total_cost = 0.0
            
            for event in events:
                event_type = event.event_type
                if event_type not in totals_by_type:
                    totals_by_type[event_type] = {
                        "count": 0,
                        "cost": 0.0
                    }
                totals_by_type[event_type]["count"] += event.quantity
                totals_by_type[event_type]["cost"] += event.total_cost
                total_cost += event.total_cost
            
            ***REMOVED*** Add base subscription
            base_cost = self.BASE_SUBSCRIPTION_PRICE
            grand_total = base_cost + total_cost
            
            return {
                "success": True,
                "billing_period": billing_period,
                "base_subscription": base_cost,
                "usage_by_type": totals_by_type,
                "total_usage_cost": total_cost,
                "grand_total": grand_total,
                "currency": "USD",
                "event_count": len(events)
            }
            
        except Exception as e:
            logger.error(f"Error getting period usage: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """
        Get pricing information for all operations.
        
        Returns:
            Dictionary with pricing information
        """
        return {
            "success": True,
            "base_subscription": self.BASE_SUBSCRIPTION_PRICE,
            "pricing": self.PRICING,
            "currency": "USD"
        }
