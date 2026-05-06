import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SIGNALS_KEY = "market_signals:list"
SIGNAL_TTL = 3600 * 24 * 7   # 7 days


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def store_signal(signal: Dict[str, Any]) -> None:
    r = _redis()
    if r:
        try:
            r.lpush(SIGNALS_KEY, json.dumps(signal))
            r.ltrim(SIGNALS_KEY, 0, 999)
            r.expire(SIGNALS_KEY, SIGNAL_TTL)
        except Exception as e:
            logger.debug("signal_store: %s", e)


def get_signals(industry: str = None, region: str = None, limit: int = 50) -> List[Dict[str, Any]]:
    out = []
    r = _redis()
    if not r:
        return out
    try:
        raw_list = r.lrange(SIGNALS_KEY, 0, limit - 1)
        for raw in raw_list or []:
            s = json.loads(raw) if isinstance(raw, str) else raw
            if industry and (s.get("industry") or "").lower() != industry.lower():
                continue
            if region and (s.get("region") or "").lower() != region.lower():
                continue
            out.append(s)
    except Exception as e:
        logger.debug("get_signals: %s", e)
    return out
