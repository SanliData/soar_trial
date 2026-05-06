"""
LEARNING: learning_engine
PURPOSE: Central API for targeting recommendations and email strategy; cache; observability; extensible for lead_scoring, conversion_prediction, deal_probability
"""
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from src.learning.performance_analyzer import analyze_campaign_success
from src.learning.targeting_optimizer import optimize_targeting
from src.learning.email_optimizer import optimize_email_strategy
from src.learning.feedback_collector import collect_campaign_feedback

logger = logging.getLogger(__name__)

LEARNING_CACHE_PREFIX = "learning:"
LEARNING_CACHE_TTL = 3600 * 24  ***REMOVED*** 24h


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def _get_db():
    from src.db.base import SessionLocal
    return SessionLocal()


def _log_learning_event(learning_run_id: str, campaign_id: Optional[str], event_type: str, analysis_time_ms: Optional[int], insight_results: Optional[Dict[str, Any]]) -> None:
    try:
        db = _get_db()
        try:
            from src.learning.models.learning_event import LearningEvent
            db.add(LearningEvent(
                learning_run_id=learning_run_id,
                campaign_id=campaign_id,
                event_type=event_type,
                analysis_time_ms=analysis_time_ms,
                insight_results=insight_results,
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug("_log_learning_event failed: %s", e)


async def get_targeting_recommendations(
    industry: str,
    location: Optional[str] = None,
    roles: Optional[List[str]] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Return targeting suggestions (recommended_roles, recommended_company_size, etc.) for the AI Sales Agent.
    Cached by (industry, location) for fast retrieval.
    """
    cache_key = f"{LEARNING_CACHE_PREFIX}targeting:{industry}:{location or 'all'}"
    redis = _get_redis()
    if use_cache and redis:
        try:
            raw = redis.get(cache_key)
            if raw:
                return json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            logger.debug("get_targeting_recommendations cache get: %s", e)

    run_id = f"learn_{uuid.uuid4().hex[:12]}"
    t0 = time.perf_counter()
    try:
        out = await optimize_targeting(industry=industry, location=location, roles=roles)
        analysis_time_ms = int((time.perf_counter() - t0) * 1000)
        _log_learning_event(run_id, None, "get_targeting_recommendations", analysis_time_ms, out)
        if redis:
            try:
                redis.setex(cache_key, LEARNING_CACHE_TTL, json.dumps(out))
            except Exception as e:
                logger.debug("get_targeting_recommendations cache set: %s", e)
        return out
    except Exception as e:
        logger.warning("get_targeting_recommendations failed: %s", e)
        return {
            "recommended_roles": roles or ["CTO", "VP Infrastructure", "Operations Director"],
            "recommended_company_size": "50-200 employees",
            "recommended_industries": [industry],
            "recommended_location": location,
            "based_on_campaigns": 0,
        }


async def get_email_strategy(
    campaign_goal: Optional[str] = None,
    industry: Optional[str] = None,
    past_successful_emails: Optional[List[Dict[str, Any]]] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Return email strategy (subject_template, email_template, style) for the AI Sales Agent.
    Cached by campaign_goal/industry for fast retrieval.
    """
    cache_key = f"{LEARNING_CACHE_PREFIX}email_strategy:{campaign_goal or 'default'}:{industry or 'all'}"
    redis = _get_redis()
    if use_cache and redis and not past_successful_emails:
        try:
            raw = redis.get(cache_key)
            if raw:
                return json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            logger.debug("get_email_strategy cache get: %s", e)

    run_id = f"learn_{uuid.uuid4().hex[:12]}"
    t0 = time.perf_counter()
    campaign_context = {"goal": campaign_goal, "industry": industry}
    try:
        out = await optimize_email_strategy(
            past_successful_emails=past_successful_emails,
            campaign_context=campaign_context,
        )
        analysis_time_ms = int((time.perf_counter() - t0) * 1000)
        _log_learning_event(run_id, None, "get_email_strategy", analysis_time_ms, {"style": out.get("style")})
        if redis and not past_successful_emails:
            try:
                redis.setex(cache_key, LEARNING_CACHE_TTL, json.dumps(out))
            except Exception as e:
                logger.debug("get_email_strategy cache set: %s", e)
        return out
    except Exception as e:
        logger.warning("get_email_strategy failed: %s", e)
        return {
            "subject_template": "Re: {{topic}} – quick question",
            "email_template": "Hi {{first_name}},\n\nI noticed {{company}} is active in {{industry}}. We help with {{goal}}. Open to a short call?\n\nBest,\n{{sender}}",
            "style": "short problem-solution",
        }


async def run_learning_loop_for_campaign(campaign_id: str) -> Dict[str, Any]:
    """
    Background learning loop: collect feedback (caller provides metrics) -> analyze -> update strategies.
    Enqueue via Redis for background processing; do not block.
    """
    run_id = f"learn_{uuid.uuid4().hex[:12]}"
    redis = _get_redis()
    if redis:
        try:
            redis.lpush("learning:analyze_queue", campaign_id)
            _log_learning_event(run_id, campaign_id, "analyze_campaign_queued", None, {"campaign_id": campaign_id})
            return {"queued": True, "campaign_id": campaign_id}
        except Exception as e:
            logger.warning("run_learning_loop_for_campaign queue failed: %s", e)
    ***REMOVED*** Sync fallback: just run analysis
    t0 = time.perf_counter()
    insights = await analyze_campaign_success(limit=50)
    analysis_time_ms = int((time.perf_counter() - t0) * 1000)
    _log_learning_event(run_id, campaign_id, "analyze_campaign", analysis_time_ms, insights)
    return {"queued": False, "campaign_id": campaign_id, "insights": insights}


***REMOVED*** Extensibility: placeholders for future models
async def get_lead_scoring_model(contact: Dict[str, Any], campaign_context: Dict[str, Any]) -> float:
    """Placeholder for lead_scoring_model. Returns 0.0–1.0 score."""
    return 0.5


async def get_conversion_prediction(campaign_id: str, contact_ids: List[str]) -> Dict[str, float]:
    """Placeholder for conversion_prediction_model. Returns contact_id -> probability."""
    return {c: 0.5 for c in contact_ids}


async def get_deal_probability(contact_id: str, stage: str) -> float:
    """Placeholder for deal_probability_model."""
    return 0.5
