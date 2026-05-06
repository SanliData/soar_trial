"""
OPPORTUNITY_ENGINE: recommendation_engine
PURPOSE: Combine detected opportunities, scoring, persona selection → final ranked sales opportunities.
"""
import logging
from typing import Any, Dict, List, Optional

from src.opportunity_engine.models.opportunity import Opportunity
from src.opportunity_engine.models.opportunity_score import OpportunityScore
from src.opportunity_engine.opportunity_detector import detect_opportunities
from src.opportunity_engine.opportunity_ranker import rank_opportunities
from src.opportunity_engine.opportunity_store import get_recommendations_cached, store_recommendations

logger = logging.getLogger(__name__)


def get_recommendations(
    industry: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 20,
    use_cache: bool = True,
    db_session: Any = None,
) -> Dict[str, Any]:
    """
    Full pipeline: detect → score (with persona) → rank → optional cache.
    Returns final ranked recommendations with company, score, recommended_persona, confidence.
    """
    if use_cache:
        cached = get_recommendations_cached(industry or "", region or "")
        if cached:
            return _format_response(industry, region, cached[:limit])
    candidates: List[Opportunity] = detect_opportunities(industry=industry, region=region, limit=limit * 2, db_session=db_session)
    if not candidates:
        return _format_response(industry, region, [])
    scored: List[OpportunityScore] = rank_opportunities(candidates, limit=limit)
    if scored:
        store_recommendations(scored, industry or "", region or "")
    return _format_response(industry, region, scored)


def _format_response(industry: Optional[str], region: Optional[str], recs: List[OpportunityScore]) -> Dict[str, Any]:
    out = {
        "industry": industry or "",
        "region": region or "",
        "recommended_opportunities": [
            {
                "company": r.company,
                "company_id": r.company_id,
                "industry": r.industry,
                "region": r.region,
                "score": r.score,
                "recommended_persona": r.recommended_persona,
                "confidence": r.confidence,
                "signals": r.signals,
                "score_breakdown": r.score_breakdown,
            }
            for r in recs
        ],
    }
    return out
