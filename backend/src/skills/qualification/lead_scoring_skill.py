"""
SKILLS: lead_scoring_skill (unified)
PURPOSE: Score leads/companies by fit and engagement signals; output scores for prioritization
"""
import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class LeadScoringSkill(BaseSkill):
    name = "lead_scoring"
    description = "Score leads or companies by fit and engagement; output scored list"
    inputs = ["companies", "leads", "weights"]
    outputs = ["scored_leads", "scored_companies"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        leads = context.get("leads", [])
        weights = context.get("weights") or {"industry_fit": 0.3, "role_fit": 0.3, "engagement": 0.4}
        scored_companies: List[Dict[str, Any]] = []
        scored_leads: List[Dict[str, Any]] = []
        get_persona_scores = None
        get_industry_rates = None
        try:
            from src.campaign_learning.industry_performance_model import get_industry_rates
        except ImportError:
            pass
        try:
            from src.campaign_learning.persona_performance_model import get_persona_scores
        except ImportError:
            pass
        industry_rates = {}
        if get_industry_rates:
            try:
                industry_rates = get_industry_rates() or {}
            except Exception:
                pass
        for c in companies:
            industry = c.get("industry", "")
            score = float(industry_rates.get(industry, 0.5)) * (weights.get("industry_fit", 0.3) or 0.3)
            contacts = c.get("selected_contacts", c.get("contacts", []))
            if contacts and get_persona_scores:
                try:
                    role_scores = get_persona_scores() or {}
                    for contact in contacts:
                        role = (contact.get("role") or "").strip()
                        score += (role_scores.get(role, 0.5) or 0.5) * (weights.get("role_fit", 0.3) or 0.3) / max(len(contacts), 1)
                except Exception:
                    score += 0.3
            else:
                score += 0.3
            scored_companies.append({**c, "score": round(min(1.0, score), 3)})
        scored_companies.sort(key=lambda x: -x.get("score", 0))
        for lead in leads:
            industry = lead.get("industry", "")
            score = float(industry_rates.get(industry, 0.5)) * weights.get("industry_fit", 0.3) + 0.3
            scored_leads.append({**lead, "score": round(min(1.0, score), 3)})
        scored_leads.sort(key=lambda x: -x.get("score", 0))
        logger.info("lead_scoring: %s companies, %s leads", len(scored_companies), len(scored_leads))
        return {"scored_companies": scored_companies, "scored_leads": scored_leads}
