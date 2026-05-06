"""
MARKET_SIGNALS: signal_weights
PURPOSE: Configurable weights per signal type for opportunity scoring; runtime updates via Redis
"""
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

REDIS_KEY = "market_signals:signal_weights"
REDIS_TTL = 86400 * 7   # 7 days

# Default weights (used when Redis has no override)
SIGNAL_WEIGHTS = {
    "hiring_spike": 0.6,
    "funding_event": 0.8,
    "industry_engagement": 0.7,
    "technology_adoption": 0.65,
    "similar_company_response": 0.75,
    "geographic_engagement_cluster": 0.7,
    "industry_reply_rate_increase": 0.72,
    "company_expansion": 0.68,
}


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def get_signal_weights() -> Dict[str, float]:
    """
    Return current signal weights. Uses Redis-stored config if present, else SIGNAL_WEIGHTS.
    Opportunity scoring must use these weights for market signal contribution.
    """
    r = _redis()
    if r:
        try:
            raw = r.get(REDIS_KEY)
            if raw:
                data = json.loads(raw) if isinstance(raw, str) else raw
                if isinstance(data, dict):
                    out = dict(SIGNAL_WEIGHTS)
                    out.update({k: float(v) for k, v in data.items() if isinstance(v, (int, float))})
                    return out
        except Exception as e:
            logger.debug("get_signal_weights: %s", e)
    return dict(SIGNAL_WEIGHTS)


def set_signal_weights(weights: Dict[str, float]) -> bool:
    """
    Update signal weights at runtime (persist to Redis). Merges with defaults.
    """
    r = _redis()
    if not r:
        return False
    try:
        current = get_signal_weights()
        current.update(weights)
        r.setex(REDIS_KEY, REDIS_TTL, json.dumps(current))
        return True
    except Exception as e:
        logger.debug("set_signal_weights: %s", e)
        return False


def get_weight_for_signal(signal_type: str) -> float:
    """Return weight for a single signal type (default 0.6 if unknown)."""
    return get_signal_weights().get(signal_type, 0.6)
