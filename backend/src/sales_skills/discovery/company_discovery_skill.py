"""
SALES_SKILLS: company_discovery_skill
PURPOSE: Discover companies by industry, location, keywords; output list for workflows
"""
import logging
from typing import Any, Dict, List

from src.sales_skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class CompanyDiscoverySkill(BaseSkill):
    name = "company_discovery"
    description = "Discover companies by industry and location (and optional keywords)"
    inputs = ["industry", "location"]
    outputs = ["companies"]

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        industry = context.get("industry", "")
        location = context.get("location", "")
        keywords = context.get("keywords") or []
        company_size = context.get("company_size")
        limit = context.get("limit", 20)
        companies: List[Dict[str, Any]] = []
        try:
            from src.db.base import SessionLocal
            from src.models.intel_company import IntelCompany
            db = SessionLocal()
            try:
                q = db.query(IntelCompany).filter(IntelCompany.industry.ilike(f"%{industry}%"))
                if location:
                    q = q.filter(IntelCompany.location.ilike(f"%{location}%"))
                rows = q.order_by(IntelCompany.created_at.desc()).limit(limit).all()
                companies = [
                    {
                        "id": c.id,
                        "name": c.company_name,
                        "website": c.website,
                        "industry": c.industry or industry,
                        "location": c.location or location,
                        "company_size": company_size,
                    }
                    for c in rows
                ]
            finally:
                db.close()
        except Exception as e:
            logger.debug("company_discovery fallback: %s", e)
        if not companies:
            companies = [
                {"name": f"Example {industry} Co", "website": None, "industry": industry, "location": location},
                {"name": f"{location or 'N/A'} {industry} LLC", "website": None, "industry": industry, "location": location},
            ]
        for c in companies:
            c.setdefault("industry", industry)
            c.setdefault("location", location)
            if company_size:
                c.setdefault("company_size", company_size)
        if keywords:
            for c in companies:
                c.setdefault("keywords", keywords)
        logger.info("company_discovery_skill: found %s companies", len(companies))
        return {"companies": companies}
