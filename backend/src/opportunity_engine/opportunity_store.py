import json
import logging
from typing import List

from src.opportunity_engine.models.opportunity_score import OpportunityScore

logger = logging.getLogger(__name__)
STORE_PREFIX = "opportunity_engine:"
STORE_TTL = 3600


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def _key(industry: str = "", region: str = "") -> str:
    return "%srecs:%s:%s" % (STORE_PREFIX, industry or "all", region or "all")


def store_recommendations(recommendations: List[OpportunityScore], industry: str = "", region: str = "") -> None:
    r = _redis()
    if r:
        try:
            r.setex(_key(industry, region), STORE_TTL, json.dumps([s.model_dump() for s in recommendations]))
        except Exception as e:
            logger.debug("opportunity_store store: %s", e)


def get_recommendations_cached(industry: str = "", region: str = "") -> List[OpportunityScore]:
    r = _redis()
    if not r:
        return []
    try:
        raw = r.get(_key(industry, region))
        if not raw:
            return []
        data = json.loads(raw) if isinstance(raw, str) else raw
        return [OpportunityScore(**item) for item in data]
    except Exception as e:
        logger.debug("opportunity_store get: %s", e)
        return []
