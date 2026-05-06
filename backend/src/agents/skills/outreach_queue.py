"""
AGENTS: outreach_queue skill
PURPOSE: Finalize outreach (store to Redis queue or return summary); structured output
"""
import json
import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


async def run_outreach_queue(
    companies: List[Dict[str, Any]],
    campaign_goal: str,
    agent_run_id: str,
) -> Dict[str, Any]:
    """
    Push generated leads/emails to Redis queue (when available) and return summary.
    Returns { "companies": companies, "queued": true|false, "summary": {...} }
    """
    logger.info("agent skill: outreach_queue start companies=%s run_id=%s", len(companies), agent_run_id)
    start = time.perf_counter()
    redis = _get_redis()
    total_emails = sum(len(c.get("contacts", [])) for c in companies)
    summary = {
        "companies_count": len(companies),
        "leads_count": sum(len(c.get("contacts", [])) for c in companies),
        "emails_count": total_emails,
    }
    queued = False
    if redis:
        try:
            key = f"agents:outreach:{agent_run_id}"
            payload = {"campaign_goal": campaign_goal, "companies": companies}
            redis.setex(key, 86400 * 7, json.dumps(payload))
            redis.lpush("agents:outreach:queue", agent_run_id)
            queued = True
        except Exception as e:
            logger.warning("outreach_queue Redis push failed: %s", e)
    latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info("agent skill: outreach_queue done queued=%s latency_ms=%s", queued, latency_ms)
    return {"companies": companies, "queued": queued, "summary": summary, "latency_ms": latency_ms}
