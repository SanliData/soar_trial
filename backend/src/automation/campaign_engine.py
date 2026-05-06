"""
AUTOMATION: campaign_engine
PURPOSE: start_campaign, pause_campaign, campaign_status; Redis queue for background processing
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


async def start_campaign(
    campaign_id: str,
    campaign_goal: str,
    companies: List[Dict[str, Any]],
    agent_run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Enqueue campaign to Redis for background workers (outreach send, response handling).
    If campaign_id already exists in DB (IntelCampaign), only enqueue; else caller must create it first.
    """
    redis = _get_redis()
    if not redis:
        return {"status": "error", "message": "Redis not available", "campaign_id": campaign_id}
    try:
        payload = {"campaign_id": campaign_id, "agent_run_id": agent_run_id, "goal": campaign_goal, "companies": companies}
        redis.setex(f"automation:campaign:{campaign_id}", 86400 * 7, json.dumps(payload))
        redis.lpush("automation:campaign:queue", campaign_id)
        redis.hset("automation:campaign:status", campaign_id, "queued")
        return {"status": "queued", "campaign_id": campaign_id, "message": "Campaign enqueued"}
    except Exception as e:
        logger.warning("start_campaign failed: %s", e)
        return {"status": "error", "message": str(e), "campaign_id": campaign_id}


async def pause_campaign(campaign_id: str) -> Dict[str, Any]:
    """Set campaign status to paused (Redis + DB)."""
    redis = _get_redis()
    if redis:
        try:
            redis.hset("automation:campaign:status", campaign_id, "paused")
        except Exception as e:
            logger.warning("pause_campaign Redis failed: %s", e)
    try:
        from src.db.base import SessionLocal
        from src.models.intel_campaign import IntelCampaign
        db = SessionLocal()
        try:
            c = db.query(IntelCampaign).filter(IntelCampaign.campaign_id == campaign_id).first()
            if c:
                c.status = "paused"
                db.commit()
                return {"status": "paused", "campaign_id": campaign_id}
        finally:
            db.close()
    except Exception as e:
        logger.warning("pause_campaign DB failed: %s", e)
    return {"status": "paused", "campaign_id": campaign_id}


async def campaign_status(campaign_id: str) -> Dict[str, Any]:
    """Return campaign status and counts from Redis and/or DB."""
    out = {"campaign_id": campaign_id, "status": None, "goal": None, "companies_count": None, "contacts_count": None}
    redis = _get_redis()
    if redis:
        try:
            status = redis.hget("automation:campaign:status", campaign_id)
            if status:
                out["status"] = status.decode() if isinstance(status, bytes) else status
            raw = redis.get(f"automation:campaign:{campaign_id}")
            if raw:
                data = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
                out["goal"] = data.get("goal")
                companies = data.get("companies", [])
                out["companies_count"] = len(companies)
                out["contacts_count"] = sum(len(c.get("contacts", [])) for c in companies)
        except Exception as e:
            logger.debug("campaign_status Redis: %s", e)
    try:
        from src.db.base import SessionLocal
        from src.models.intel_campaign import IntelCampaign
        db = SessionLocal()
        try:
            c = db.query(IntelCampaign).filter(IntelCampaign.campaign_id == campaign_id).first()
            if c:
                out["status"] = out["status"] or c.status
                out["goal"] = out["goal"] or c.goal
                if c.payload:
                    out["companies_count"] = out["companies_count"] or c.payload.get("companies_count")
                    out["contacts_count"] = out["contacts_count"] or c.payload.get("contacts_count")
        finally:
            db.close()
    except Exception as e:
        logger.debug("campaign_status DB: %s", e)
    return out


async def get_campaign_status(campaign_id: str) -> Optional[Dict[str, Any]]:
    """Alias for campaign_status; returns None if not found."""
    result = await campaign_status(campaign_id)
    if result.get("status") is None and result.get("goal") is None:
        return None
    return result
