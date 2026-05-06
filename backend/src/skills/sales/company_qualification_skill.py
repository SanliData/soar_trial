import logging
from typing import Any, Dict
from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class CompanyQualificationSkill(BaseSkill):
    name = "company_qualification_skill"
    description = "Score companies"
    inputs = ["companies"]
    outputs = ["companies", "scores"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        scores = [{"company_id": c.get("id"), "score": 0.5} for c in companies]
        try:
            from src.campaign_learning.industry_performance_model import get_industry_rates
            rates = get_industry_rates()
            for i, c in enumerate(companies):
                if i < len(scores):
                    scores[i]["score"] = round(float(rates.get(c.get("industry") or "", 0.5)), 3)
        except Exception:
            pass
        return {"companies": companies, "scores": scores}
