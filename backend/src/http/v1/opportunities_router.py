import logging
from typing import Any

from fastapi import APIRouter, Query, HTTPException

from src.opportunity_engine.recommendation_engine import get_recommendations
from src.opportunity_engine.opportunity_explain import explain_opportunity

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.get("/recommendations")
async def recommendations(
    industry: str = Query(None, description="Industry filter (optional for all)"),
    region: str = Query(None),
    limit: int = Query(20, le=100),
    use_cache: bool = Query(True),
) -> dict:
    """GET /opportunities/recommendations?industry=fiber+infrastructure&region=Texas. Returns ranked opportunities with score, recommended_persona, confidence."""
    result = get_recommendations(industry=industry, region=region, limit=limit, use_cache=use_cache)
    return result


@router.get("/explain/{company_id}")
async def explain_company_opportunity(company_id: int) -> dict:
    """
    GET /opportunities/explain/{company_id}.
    Returns score explanation: company, score, score_breakdown (industry_performance, persona_success, market_signals, company_similarity), signals.
    """
    result = explain_opportunity(company_id=company_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Company not found or could not compute score")
    return result
