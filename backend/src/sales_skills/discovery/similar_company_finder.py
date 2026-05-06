"""
SALES_SKILLS: similar_company_finder
PURPOSE: Find companies similar to a reference company (by id or industry/location)
"""
import logging
from typing import Any, Dict, List

from src.sales_skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class SimilarCompanyFinderSkill(BaseSkill):
    name = "similar_company_finder"
    description = "Find companies similar to a reference company or industry/location"
    inputs = ["company_id", "industry", "location", "limit"]
    outputs = ["similar_companies"]

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        company_id = context.get("company_id")
        industry = context.get("industry")
        location = context.get("location")
        limit = context.get("limit", 20)
        similar: List[Dict[str, Any]] = []
        try:
            from src.db.base import SessionLocal
            from src.models.intel_company import IntelCompany
            db = SessionLocal()
            try:
                if company_id:
                    ref = db.query(IntelCompany).filter(IntelCompany.id == company_id).first()
                    if ref:
                        industry = industry or ref.industry
                        location = location or ref.location
                q = db.query(IntelCompany)
                if industry:
                    q = q.filter(IntelCompany.industry.ilike(f"%{industry}%"))
                if location:
                    q = q.filter(IntelCompany.location.ilike(f"%{location}%"))
                if company_id:
                    q = q.filter(IntelCompany.id != company_id)
                rows = q.order_by(IntelCompany.created_at.desc()).limit(limit).all()
                similar = [
                    {"id": c.id, "company_name": c.company_name, "website": c.website, "industry": c.industry, "location": c.location}
                    for c in rows
                ]
            finally:
                db.close()
        except Exception as e:
            logger.debug("similar_company_finder: %s", e)
        logger.info("similar_company_finder: found %s companies", len(similar))
        return {"similar_companies": similar}
