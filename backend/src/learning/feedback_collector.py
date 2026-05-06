"""
LEARNING: feedback_collector
PURPOSE: Record email responses, campaign performance, contact engagement; update campaign metrics
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

LEARNING_CACHE_PREFIX = "learning:"
LEARNING_CACHE_TTL = 3600 * 24   # 24h for recommendations cache


def _get_db():
    from src.db.base import SessionLocal
    return SessionLocal()


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


async def collect_campaign_feedback(
    campaign_id: str,
    emails_sent: int,
    emails_opened: int = 0,
    replies_received: int = 0,
    positive_responses: int = 0,
    meetings_booked: int = 0,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    roles_snapshot: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Record campaign performance and upsert campaign_metrics.
    Call this when campaign data is available (e.g. from webhooks or manual reporting).
    """
    db = _get_db()
    try:
        from src.learning.models.campaign_metrics import CampaignMetrics
        existing = db.query(CampaignMetrics).filter(CampaignMetrics.campaign_id == campaign_id).first()
        roles_str = json.dumps(roles_snapshot) if roles_snapshot else None
        if existing:
            existing.emails_sent = emails_sent
            existing.emails_opened = emails_opened
            existing.replies_received = replies_received
            existing.positive_responses = positive_responses
            existing.meetings_booked = meetings_booked
            if industry is not None:
                existing.industry = industry
            if location is not None:
                existing.location = location
            if roles_snapshot is not None:
                existing.roles_snapshot = roles_str
            db.commit()
            logger.info("learning: updated campaign_metrics campaign_id=%s", campaign_id)
            return {"updated": True, "campaign_id": campaign_id}
        else:
            m = CampaignMetrics(
                campaign_id=campaign_id,
                emails_sent=emails_sent,
                emails_opened=emails_opened,
                replies_received=replies_received,
                positive_responses=positive_responses,
                meetings_booked=meetings_booked,
                industry=industry,
                location=location,
                roles_snapshot=roles_str,
            )
            db.add(m)
            db.commit()
            logger.info("learning: created campaign_metrics campaign_id=%s", campaign_id)
            return {"created": True, "campaign_id": campaign_id}
    except Exception as e:
        logger.exception("collect_campaign_feedback failed: %s", e)
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


async def record_email_response(
    campaign_id: str,
    contact_id: Optional[str] = None,
    classification: Optional[str] = None,
    opened: bool = False,
) -> None:
    """
    Record a single email response (open or reply). Can be called from webhooks.
    Updates metrics by incrementing replies_received or emails_opened; then collect_campaign_feedback
    should be called with aggregated counts, or we increment here via raw SQL / select-update.
    """
    redis = _get_redis()
    if redis:
        key = f"{LEARNING_CACHE_PREFIX}feedback:{campaign_id}"
        try:
            redis.hincrby(key, "replies_received" if classification else "emails_opened", 1)
            if classification == "positive_interest":
                redis.hincrby(key, "positive_responses", 1)
            redis.expire(key, 86400 * 7)
        except Exception as e:
            logger.debug("record_email_response Redis: %s", e)
