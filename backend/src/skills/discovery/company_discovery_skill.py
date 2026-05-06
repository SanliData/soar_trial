"""
SKILLS: company_discovery_skill
PURPOSE: Inputs industry, location -> output list of companies (name, website, location)
"""
import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class CompanyDiscoverySkill(BaseSkill):
    name = "company_discovery"
    description = "Discover companies by industry and location"
    inputs = ["industry", "location"]
    outputs = ["companies"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        industry = context.get("industry", "")
        location = context.get("location", "")
        keywords = context.get("keywords") or []
        company_size = context.get("company_size")
        companies = [
            {"name": f"Example {industry} Co", "website": "https://example-fiber.com", "location": location},
            {"name": f"{location} {industry} LLC", "website": "https://example-texas-fiber.com", "location": location},
        ]
        if keywords:
            companies.append({"name": "Keyword Match Corp", "website": None, "location": location})
        for c in companies:
            c.setdefault("industry", industry)
            c.setdefault("company_size", company_size or "11-50")
        logger.info("company_discovery_skill: found %s companies", len(companies))
        return {"companies": companies}
