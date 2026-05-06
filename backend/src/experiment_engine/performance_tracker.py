"""
EXPERIMENT_ENGINE: performance_tracker
PURPOSE: Record reply_rate, open_rate, click_rate per experiment/variant for A/B analysis
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REDIS_KEY_PREFIX = "experiment_engine:metrics"
REDIS_TTL = 86400 * 90   # 90 days
EVENT_TYPES = ("sent", "opened", "clicked", "replied")


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def record_event(
    experiment_id: str,
    variant_id: str,
    event_type: str,
    campaign_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    value: float = 1.0,
) -> bool:
    """
    Record a performance event. event_type: sent | opened | clicked | replied.
    Used to compute open_rate, click_rate, reply_rate per variant.
    """
    if event_type not in EVENT_TYPES:
        logger.warning("performance_tracker: unknown event_type %s", event_type)
        return False
    r = _redis()
    if not r:
        return False
    key = f"{REDIS_KEY_PREFIX}:{experiment_id}:{variant_id}:{event_type}"
    try:
        r.incrbyfloat(key, value)
        r.expire(key, REDIS_TTL)
        return True
    except Exception as e:
        logger.debug("record_event: %s", e)
        return False


def get_metrics(experiment_id: str) -> Dict[str, Any]:
    """
    Get aggregated metrics per variant: sent, opened, clicked, replied counts;
    derived open_rate, click_rate, reply_rate.
    """
    r = _redis()
    if not r:
        return {"experiment_id": experiment_id, "variants": {}}
    out = {"experiment_id": experiment_id, "variants": {}}
    try:
        from src.experiment_engine.experiment_manager import get_experiment
        ex = get_experiment(experiment_id)
        if not ex:
            return out
        for v in ex.get("variants", []):
            vid = v.get("id", "unknown")
            counts = {}
            for et in EVENT_TYPES:
                k = f"{REDIS_KEY_PREFIX}:{experiment_id}:{vid}:{et}"
                raw = r.get(k)
                counts[et] = float(raw) if raw else 0.0
            sent = counts.get("sent", 0) or 1
            out["variants"][vid] = {
                **counts,
                "open_rate": round(counts.get("opened", 0) / sent, 4),
                "click_rate": round(counts.get("clicked", 0) / sent, 4),
                "reply_rate": round(counts.get("replied", 0) / sent, 4),
            }
    except Exception as e:
        logger.debug("get_metrics: %s", e)
    return out


def get_experiment_metrics(experiment_id: str) -> Dict[str, Any]:
    """Alias for get_metrics."""
    return get_metrics(experiment_id)
