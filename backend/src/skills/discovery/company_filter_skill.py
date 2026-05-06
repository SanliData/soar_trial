"""
SKILLS: company_filter_skill
PURPOSE: Filter companies by relevance_score, industry match, or size; reduce set for downstream steps
"""
import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class CompanyFilterSkill(BaseSkill):
    name = "company_filter"
    description = "Filter companies by relevance score and optional criteria"
    inputs = ["companies"]
    outputs = ["companies"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        min_relevance = float(context.get("min_relevance_score", 0.0))
        max_companies = int(context.get("max_companies", 100))
        industry_filter = context.get("industry_filter")  ***REMOVED*** optional: keep only if match
        out = []
        for c in companies:
            score = float(c.get("relevance_score", 0.5))
            if score < min_relevance:
                continue
            if industry_filter and c.get("industry") and industry_filter.lower() not in (c.get("industry") or "").lower():
                continue
            out.append(c)
        out = out[:max_companies]
        logger.info("company_filter_skill: %s -> %s companies", len(companies), len(out))
        return {"companies": out}
