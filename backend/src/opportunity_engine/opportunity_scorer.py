"""
OPPORTUNITY_ENGINE: opportunity_scorer
PURPOSE: Score accounts/leads as next-best opportunities using industry fit, persona fit, engagement
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def score_single_opportunity(
    company: Dict[str, Any],
    industry_rates: Optional[Dict[str, float]] = None,
    persona_scores: Optional[Dict[str, float]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Score one company/lead (0..1). Uses industry reply rate and contact role scores when available.
    """
    w = weights or {"industry_fit": 0.4, "persona_fit": 0.4, "engagement": 0.2}
    industry_rates = industry_rates or {}
    persona_scores = persona_scores or {}
    industry = (company.get("industry") or "").strip()
    score = 0.0
    if industry and industry_rates:
        score += float(industry_rates.get(industry, 0.5)) * (w.get("industry_fit") or 0.4)
    else:
        score += 0.5 * (w.get("industry_fit") or 0.4)
    contacts = company.get("selected_contacts") or company.get("contacts") or []
    if contacts and persona_scores:
        role_score = 0.0
        for c in contacts:
            role = (c.get("role") or "").strip()
            role_score += float(persona_scores.get(role, 0.5))
        score += (role_score / len(contacts)) * (w.get("persona_fit") or 0.4)
    else:
        score += 0.5 * (w.get("persona_fit") or 0.4)
    score += 0.5 * (w.get("engagement") or 0.2)
    return round(min(1.0, score), 4)


def score_opportunities(
    companies: List[Dict[str, Any]],
    industry_rates: Optional[Dict[str, float]] = None,
    persona_scores: Optional[Dict[str, float]] = None,
    weights: Optional[Dict[str, float]] = None,
) -> List[Dict[str, Any]]:
    """Score each company and return list of { ...company, score }. Fetches industry/persona rates if not provided."""
    if industry_rates is None or persona_scores is None:
        try:
            from src.campaign_learning.industry_performance_model import get_industry_rates
            from src.campaign_learning.persona_performance_model import get_persona_scores
            if industry_rates is None:
                industry_rates = get_industry_rates()
            if persona_scores is None:
                persona_scores = get_persona_scores()
        except ImportError:
            industry_rates = industry_rates or {}
            persona_scores = persona_scores or {}
    out = []
    for c in companies:
        s = score_single_opportunity(c, industry_rates=industry_rates, persona_scores=persona_scores, weights=weights)
        out.append({**c, "score": s})
    return out
