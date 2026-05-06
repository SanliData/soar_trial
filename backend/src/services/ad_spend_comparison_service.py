"""
SERVICE: ad_spend_comparison_service
PURPOSE: Compare SOAR spend vs traditional ad spend
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from src.services.usage_billing_service import UsageBillingService

logger = logging.getLogger(__name__)


class AdSpendComparisonService:
    """
    Service for comparing SOAR usage costs vs traditional ad spend.
    Uses industry and region benchmarks.
    """
    
    # Industry benchmarks for traditional ad spend (CPC/CPM estimates)
    # These are estimated averages - clearly labeled as estimates
    INDUSTRY_BENCHMARKS = {
        "default": {
            "cpc": 2.50,   # Average CPC
            "cpm": 10.00,   # Average CPM
            "conversion_rate": 0.02,   # 2% average conversion rate
        },
        "b2b": {
            "cpc": 3.50,
            "cpm": 15.00,
            "conversion_rate": 0.015,   # 1.5% for B2B
        },
        "saas": {
            "cpc": 4.00,
            "cpm": 18.00,
            "conversion_rate": 0.02,
        },
        "manufacturing": {
            "cpc": 2.00,
            "cpm": 8.00,
            "conversion_rate": 0.025,
        },
        "healthcare": {
            "cpc": 5.00,
            "cpm": 20.00,
            "conversion_rate": 0.015,
        },
    }
    
    # Regional multipliers (base: US)
    REGIONAL_MULTIPLIERS = {
        "US": 1.0,
        "CA": 0.9,
        "UK": 0.95,
        "EU": 0.85,
        "TR": 0.6,
        "ASIA": 0.7,
        "LATAM": 0.5,
        "default": 1.0,
    }
    
    def __init__(self, db: Session):
        """Initialize Ad Spend Comparison Service with database session."""
        self.db = db
        self.usage_billing_service = UsageBillingService(db)
    
    def estimate_traditional_ad_spend(
        self,
        user_id: int,
        billing_period: Optional[str] = None,
        industry: str = "b2b",
        region: str = "US"
    ) -> Dict[str, Any]:
        """
        Estimate what traditional ad spend would cost for equivalent results.
        
        Args:
            user_id: User ID
            billing_period: Billing period (YYYY-MM). If None, uses current period.
            industry: Industry type (b2b, saas, manufacturing, healthcare, default)
            region: Region (US, CA, UK, EU, TR, ASIA, LATAM, default)
        
        Returns:
            Dictionary with estimated ad spend comparison
        """
        try:
            # Get SOAR usage
            usage_summary = self.usage_billing_service.get_period_usage(
                user_id=user_id,
                billing_period=billing_period
            )
            
            if not usage_summary.get("success"):
                return usage_summary
            
            # Get benchmarks
            industry_bench = self.INDUSTRY_BENCHMARKS.get(
                industry,
                self.INDUSTRY_BENCHMARKS["default"]
            )
            regional_mult = self.REGIONAL_MULTIPLIERS.get(
                region,
                self.REGIONAL_MULTIPLIERS["default"]
            )
            
            # Adjust benchmarks by region
            cpc = industry_bench["cpc"] * regional_mult
            cpm = industry_bench["cpm"] * regional_mult
            conversion_rate = industry_bench["conversion_rate"]
            
            # Estimate traditional ad spend
            # For each booked meeting, estimate how many clicks/impressions needed
            usage_by_type = usage_summary.get("usage_by_type", {})
            booked_meetings = usage_by_type.get("booked_meeting", {}).get("count", 0)
            
            # Estimate clicks needed (inverse of conversion rate)
            if conversion_rate > 0:
                estimated_clicks = booked_meetings / conversion_rate
            else:
                estimated_clicks = 0
            
            # Estimate impressions (assuming 2% CTR)
            ctr = 0.02   # 2% click-through rate
            if ctr > 0:
                estimated_impressions = estimated_clicks / ctr
            else:
                estimated_impressions = 0
            
            # Calculate estimated ad spend
            estimated_cpc_cost = estimated_clicks * cpc
            estimated_cpm_cost = (estimated_impressions / 1000) * cpm
            estimated_ad_spend = min(estimated_cpc_cost, estimated_cpm_cost)   # Use lower estimate
            
            # SOAR spend
            soar_spend = usage_summary.get("grand_total", 0)
            
            # Calculate waste reduction
            if estimated_ad_spend > 0:
                waste_reduction = ((estimated_ad_spend - soar_spend) / estimated_ad_spend) * 100
            else:
                waste_reduction = 0
            
            return {
                "success": True,
                "billing_period": usage_summary.get("billing_period"),
                "soar_spend": soar_spend,
                "estimated_traditional_ad_spend": estimated_ad_spend,
                "waste_reduction_percent": round(waste_reduction, 2),
                "savings": max(0, estimated_ad_spend - soar_spend),
                "currency": "USD",
                "benchmarks": {
                    "industry": industry,
                    "region": region,
                    "cpc": round(cpc, 2),
                    "cpm": round(cpm, 2),
                    "conversion_rate": conversion_rate,
                },
                "estimates": {
                    "booked_meetings": booked_meetings,
                    "estimated_clicks": round(estimated_clicks, 0),
                    "estimated_impressions": round(estimated_impressions, 0),
                },
                "disclaimer": "Estimated comparison based on industry benchmarks. Actual ad spend may vary. Results are not guaranteed."
            }
            
        except Exception as e:
            logger.error(f"Error estimating traditional ad spend: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
