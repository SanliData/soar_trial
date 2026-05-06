"""
SERVICE: usage_based_pricing_service
PURPOSE: Usage-based (pay-as-you-go) pricing service
ENCODING: UTF-8 WITHOUT BOM

Replaces fixed subscription tiers with usage-based pricing model.
All pricing constants read from src.config.pricing (single source of truth).
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from src.config.pricing import (
    ACCOUNT_ACTIVATION_FEE,
    QUERY_EXECUTION_COST,
    OPTIONAL_MODULES,
    MAX_RESULTS_PER_QUERY,
    MAX_VISIT_STOPS,
    PRICING_MODEL
)
from src.core.quote_token import generate_quote_token

logger = logging.getLogger(__name__)


class UsageBasedPricingService:
    """
    Usage-based pricing service.
    All pricing is pay-as-you-go, no fixed subscription tiers.
    Reads pricing constants from src.config.pricing (single source of truth).
    """
    
    ***REMOVED*** Query cap (non-negotiable unless admin override)
    MAX_QUERY_RESULTS = MAX_RESULTS_PER_QUERY  ***REMOVED*** 100
    
    def __init__(self, db: Session):
        """Initialize usage-based pricing service."""
        self.db = db
    
    def calculate_query_cost(
        self,
        include_persona_deepening: bool = False,
        include_visit_route: bool = False,
        include_export: bool = False,
        include_outreach_preparation: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate cost for a single query execution.
        
        Args:
            include_persona_deepening: Include persona deepening module
            include_visit_route: Include visit route module
            include_export: Include export module
            include_outreach_preparation: Include outreach preparation module
            
        Returns:
            Cost breakdown dictionary
        """
        base_cost = QUERY_EXECUTION_COST
        
        optional_costs = {}
        total_optional = 0.0
        
        if include_persona_deepening:
            cost = OPTIONAL_MODULES["persona_deepening"]
            optional_costs["persona_deepening"] = cost
            total_optional += cost
        
        if include_visit_route:
            cost = OPTIONAL_MODULES["visit_route"]
            optional_costs["visit_route"] = cost
            total_optional += cost
        
        if include_export:
            cost = OPTIONAL_MODULES["export"]
            optional_costs["export"] = cost
            total_optional += cost
        
        if include_outreach_preparation:
            cost = OPTIONAL_MODULES["outreach_preparation"]
            optional_costs["outreach_preparation"] = cost
            total_optional += cost
        
        total_cost = base_cost + total_optional
        
        return {
            "base_query": base_cost,
            "optional_modules": optional_costs,
            "total_optional": total_optional,
            "total_cost": total_cost,
            "currency": "USD",
            "max_results": self.MAX_QUERY_RESULTS,
            "breakdown": {
                "Query execution (max 100 businesses)": f"${base_cost:.2f}",
                **{f"{k.replace('_', ' ').title()}": f"${v:.2f}" for k, v in optional_costs.items()},
                "Total": f"${total_cost:.2f}"
            }
        }
    
    def get_account_activation_cost(self) -> Dict[str, Any]:
        """
        Get account activation fee information.
        
        Returns:
            Activation cost dictionary
        """
        return {
            "activation_fee": ACCOUNT_ACTIVATION_FEE,
            "billing_period": "monthly",
            "currency": "USD",
            "description": "Monthly account activation fee"
        }
    
    def estimate_monthly_cost(
        self,
        estimated_queries_per_month: int,
        avg_optional_modules: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Estimate monthly cost based on expected usage.
        
        Args:
            estimated_queries_per_month: Estimated number of queries per month
            avg_optional_modules: List of optional modules typically used
            
        Returns:
            Monthly cost estimate
        """
        if avg_optional_modules is None:
            avg_optional_modules = []
        
        ***REMOVED*** Calculate average cost per query
        avg_query_cost = self.calculate_query_cost(
            include_persona_deepening="persona_deepening" in avg_optional_modules,
            include_visit_route="visit_route" in avg_optional_modules,
            include_export="export" in avg_optional_modules,
            include_outreach_preparation="outreach_preparation" in avg_optional_modules
        )["total_cost"]
        
        ***REMOVED*** Monthly costs
        activation_fee = ACCOUNT_ACTIVATION_FEE
        query_costs = avg_query_cost * estimated_queries_per_month
        total_monthly = activation_fee + query_costs
        
        return {
            "activation_fee": activation_fee,
            "queries_per_month": estimated_queries_per_month,
            "avg_cost_per_query": avg_query_cost,
            "total_query_costs": query_costs,
            "total_monthly_cost": total_monthly,
            "currency": "USD",
            "breakdown": {
                "Account activation (monthly)": f"${activation_fee:.2f}",
                f"Query execution ({estimated_queries_per_month} queries × ${avg_query_cost:.2f})": f"${query_costs:.2f}",
                "Total monthly": f"${total_monthly:.2f}"
            }
        }
    
    def get_pricing_model(self) -> Dict[str, Any]:
        """
        Get complete pricing model information.
        Reads from src.config.pricing (single source of truth).
        
        Returns:
            Pricing model dictionary
        """
        return {
            "model": "usage_based",
            **PRICING_MODEL,
            "enterprise_contact": {
                "note": "For custom caps, API access, white-label, or admin override, please contact us."
            }
        }
    
    def calculate_query_cost_with_quote(
        self,
        include_persona_deepening: bool = False,
        include_visit_route: bool = False,
        include_export: bool = False,
        include_outreach_preparation: bool = False,
        max_results: int = MAX_RESULTS_PER_QUERY
    ) -> Dict[str, Any]:
        """
        Calculate cost and generate signed quote token.
        
        Args:
            include_persona_deepening: Include persona deepening module
            include_visit_route: Include visit route module
            include_export: Include export module
            include_outreach_preparation: Include outreach preparation module
            max_results: Maximum results requested (clamped to MAX_RESULTS_PER_QUERY)
            
        Returns:
            Cost breakdown with quote_token
        """
        cost_breakdown = self.calculate_query_cost(
            include_persona_deepening=include_persona_deepening,
            include_visit_route=include_visit_route,
            include_export=include_export,
            include_outreach_preparation=include_outreach_preparation
        )
        
        ***REMOVED*** Generate quote token
        quote_info = generate_quote_token(
            total_cost=cost_breakdown["total_cost"],
            include_persona_deepening=include_persona_deepening,
            include_visit_route=include_visit_route,
            include_export=include_export,
            include_outreach_preparation=include_outreach_preparation,
            max_results=max_results
        )
        
        return {
            **cost_breakdown,
            "quote_token": quote_info["quote_token"],
            "expires_at": quote_info["expires_at"],
            "request_fingerprint": quote_info["request_fingerprint"]
        }


def get_usage_based_pricing_service(db: Session) -> UsageBasedPricingService:
    """Get usage-based pricing service instance."""
    return UsageBasedPricingService(db)
