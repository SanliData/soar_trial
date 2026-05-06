import logging
from typing import Any, Dict

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class CompanyDiscoverySalesSkill(BaseSkill):
    name = "company_discovery_skill"
    description = "Discover companies by industry and location; structured JSON in/out"
    inputs = ["industry", "location", "keywords", "limit"]
    outputs = ["companies"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        industry = context.get("industry", "")
        location = context.get("location", "")
        limit = context.get("limit", 20)
        companies = []
        try:
            from src.db.base import SessionLocal
            from src.models.intel_company import IntelCompany
            db = SessionLocal()
            try:
                q = db.query(IntelCompany).filter(IntelCompany.industry.ilike("%" + (industry or "") + "%"))
                if location:
                    q = q.filter(IntelCompany.location.ilike("%" + location + "%"))
                rows = q.limit(limit).all()
                companies = [{"id": c.id, "name": c.company_name, "website": c.website, "industry": c.industry, "location": c.location} for c in rows]
            finally:
                db.close()
        except Exception as e:
            logger.exception("company_discovery_skill: %s", e)
        logger.info("company_discovery_skill: found %s companies", len(companies))
        return {"companies": companies}
