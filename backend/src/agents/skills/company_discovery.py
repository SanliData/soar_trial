"""
AGENTS: company_discovery skill
PURPOSE: Discover companies by industry, location, keywords, company size (returns structured JSON)
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def run_company_discovery(
    industry: str,
    location: str,
    keywords: Optional[List[str]] = None,
    company_size: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Discover companies matching criteria.
    Returns JSON: { "companies": [ { "name", "website", "location", "industry", "company_size" } ] }
    """
    logger.info(
        "agent skill: company_discovery start industry=%s location=%s size=%s",
        industry, location, company_size,
    )
    keywords = keywords or []
    companies = [
        {
            "name": f"Example {industry} Co",
            "website": "https://example-fiber.com",
            "location": location,
            "industry": industry,
            "company_size": company_size or "11-50",
        },
        {
            "name": f"{location} {industry} LLC",
            "website": "https://example-texas-fiber.com",
            "location": location,
            "industry": industry,
            "company_size": company_size or "51-200",
        },
    ]
    if keywords:
        companies.append({
            "name": "Keyword Match Corp",
            "website": None,
            "location": location,
            "industry": industry,
            "company_size": company_size,
        })
    result = {"companies": companies}
    logger.info("agent skill: company_discovery done count=%s", len(companies))
    return result
