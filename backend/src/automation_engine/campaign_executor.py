import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def launch_campaign(campaign_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Launch campaign; enqueue to automation queue for outreach execution."""
    try:
        from src.core.cache import get_redis_client
        r = get_redis_client()
        if r:
            import json
            r.setex("automation:campaign:%s" % campaign_id, 86400 * 7, json.dumps(payload))
            r.lpush("automation:campaign:queue", campaign_id)
            r.hset("automation:campaign:status", campaign_id, "queued")
            logger.info("launch_campaign: %s queued", campaign_id)
            return {"ok": True, "campaign_id": campaign_id, "status": "queued"}
    except Exception as e:
        logger.exception("launch_campaign: %s", e)
        return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "Redis unavailable"}
