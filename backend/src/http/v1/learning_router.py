"""
ROUTER: learning_router
PURPOSE: GET /learning/insights, GET /learning/recommendations, POST /learning/analyze-campaign
         Self-learning sales layer; background analysis via Redis queue
"""
import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.learning.performance_analyzer import analyze_campaign_success
from src.learning.learning_engine import (
    get_targeting_recommendations,
    get_email_strategy,
    run_learning_loop_for_campaign,
)
from src.learning.feedback_collector import collect_campaign_feedback

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/learning", tags=["learning"])


***REMOVED*** ---------- Response shapes (example) ----------
***REMOVED*** GET /learning/insights -> top_performing_industries, best_roles, recommended_email_style
***REMOVED*** GET /learning/recommendations -> same + targeting + email strategy
***REMOVED*** POST /learning/analyze-campaign -> queued for background analysis


class AnalyzeCampaignRequest(BaseModel):
    campaign_id: str = Field(..., description="Campaign to analyze")
    emails_sent: int = Field(0, description="Emails sent (for metrics)")
    emails_opened: int = Field(0, description="Emails opened")
    replies_received: int = Field(0, description="Replies received")
    positive_responses: int = Field(0, description="Positive interest responses")
    meetings_booked: int = Field(0, description="Meetings booked")
    industry: Optional[str] = None
    location: Optional[str] = None
    roles_snapshot: Optional[List[str]] = None


@router.get("/insights")
async def get_learning_insights():
    """
    Return learning insights: top_performing_industries, best_roles, recommended_email_style.
    Uses cached recommendations when available; does not block.
    """
    try:
        result = await analyze_campaign_success(limit=100)
        return {
            "top_performing_industries": result.get("top_industries", []),
            "best_roles": result.get("top_roles", []),
            "recommended_email_style": result.get("best_subject_style", "short problem-solution outreach"),
            "best_email_length": result.get("best_email_length", "short"),
            "campaigns_analyzed": result.get("campaigns_analyzed", 0),
        }
    except Exception as e:
        logger.warning("get_learning_insights failed: %s", e)
        raise HTTPException(status_code=503, detail="Learning insights unavailable")


@router.get("/recommendations")
async def get_learning_recommendations(
    industry: Optional[str] = None,
    location: Optional[str] = None,
    roles: Optional[str] = None,
):
    """
    Return targeting + email recommendations. Optional query: industry, location, roles (comma-separated).
    Cached for fast retrieval.
    """
    role_list = [r.strip() for r in roles.split(",")] if roles else None
    try:
        targeting = await get_targeting_recommendations(
            industry=industry or "general",
            location=location,
            roles=role_list,
        )
        email_strategy = await get_email_strategy(
            campaign_goal=None,
            industry=industry,
        )
        return {
            "top_performing_industries": targeting.get("recommended_industries", []),
            "best_roles": targeting.get("recommended_roles", []),
            "recommended_email_style": email_strategy.get("style", "short problem-solution outreach"),
            "recommended_company_size": targeting.get("recommended_company_size"),
            "subject_template": email_strategy.get("subject_template"),
            "email_template": email_strategy.get("email_template"),
        }
    except Exception as e:
        logger.warning("get_learning_recommendations failed: %s", e)
        raise HTTPException(status_code=503, detail="Recommendations unavailable")


@router.post("/analyze-campaign")
async def post_analyze_campaign(request: AnalyzeCampaignRequest):
    """
    Record campaign feedback (metrics) and enqueue campaign for learning analysis (background).
    Returns immediately; analysis runs via Redis queue. Do not block request thread.
    """
    await collect_campaign_feedback(
        campaign_id=request.campaign_id,
        emails_sent=request.emails_sent,
        emails_opened=request.emails_opened,
        replies_received=request.replies_received,
        positive_responses=request.positive_responses,
        meetings_booked=request.meetings_booked,
        industry=request.industry,
        location=request.location,
        roles_snapshot=request.roles_snapshot,
    )

    async def run_analysis():
        try:
            await run_learning_loop_for_campaign(request.campaign_id)
        except Exception as e:
            logger.exception("analyze-campaign background failed: %s", e)

    asyncio.create_task(run_analysis())

    return {
        "campaign_id": request.campaign_id,
        "status": "feedback_recorded",
        "message": "Campaign metrics recorded; analysis queued for background processing.",
    }
