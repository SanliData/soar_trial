"""
AUTOMATION: outreach_queue
PURPOSE: Schedule outreach campaigns; enqueue to Redis for background workers
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

QUEUE_KEY = "automation:outreach:queue"
PAYLOAD_PREFIX = "automation:outreach:payload:"
TTL_DAYS = 7


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


async def enqueue_outreach(
    workflow_id: str,
    campaign_goal: str,
    companies: List[Dict[str, Any]],
    campaign_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Push outreach payload to Redis for background workers. Do not block."""
    redis = _get_redis()
    if not redis:
        return {"queued": False, "workflow_id": workflow_id, "message": "Redis not available"}
    key = campaign_id or workflow_id
    payload_key = f"{PAYLOAD_PREFIX}{key}"
    payload = {"workflow_id": workflow_id, "campaign_goal": campaign_goal, "companies": companies, "campaign_id": campaign_id}
    try:
        redis.setex(payload_key, 86400 * TTL_DAYS, json.dumps(payload))
        redis.lpush(QUEUE_KEY, key)
        logger.info("outreach_queue: enqueued workflow_id=%s key=%s", workflow_id, key)
        return {"queued": True, "workflow_id": workflow_id, "payload_key": payload_key}
    except Exception as e:
        logger.warning("enqueue_outreach failed: %s", e)
        return {"queued": False, "workflow_id": workflow_id, "error": str(e)}


async def get_outreach_payload(key: str) -> Optional[Dict[str, Any]]:
    """Retrieve payload by key (for workers)."""
    redis = _get_redis()
    if not redis:
        return None
    raw = redis.get(f"{PAYLOAD_PREFIX}{key}")
    if not raw:
        return None
    try:
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None
