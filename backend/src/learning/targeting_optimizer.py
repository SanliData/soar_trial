"""
LEARNING: targeting_optimizer
PURPOSE: Use historical campaign data to recommend better targeting (roles, company_size)
"""
import logging
from typing import Any, Dict, List, Optional

from src.learning.performance_analyzer import analyze_campaign_success, identify_best_industries, identify_best_roles

logger = logging.getLogger(__name__)


async def optimize_targeting(
    industry: str,
    location: Optional[str] = None,
    roles: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Return improved targeting suggestions based on historical performance.
    Output: recommended_roles, recommended_company_size, and optional industry/location tweaks.
    """
    insights = await analyze_campaign_success(limit=100)
    best_roles = insights.get("top_roles", [])
    best_industries = insights.get("top_industries", [])

    # If user's industry is in top performers, keep; else suggest top ones
    recommended_industries = [industry] if industry in best_industries else (best_industries[:3] or [industry])
    # Prefer user's roles if they appear in best_roles; else suggest best_roles
    combined_roles = list(dict.fromkeys((roles or []) + best_roles))
    recommended_roles = [r for r in combined_roles if r in best_roles][:5]
    if not recommended_roles:
        recommended_roles = best_roles[:5] or (roles or ["CTO", "VP Infrastructure", "Operations Director"])

    return {
        "recommended_roles": recommended_roles,
        "recommended_company_size": "50-200 employees",
        "recommended_industries": recommended_industries[:3],
        "recommended_location": location,
        "based_on_campaigns": insights.get("campaigns_analyzed", 0),
    }
