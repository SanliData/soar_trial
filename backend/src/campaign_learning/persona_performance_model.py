"""
CAMPAIGN_LEARNING: persona_performance_model
PURPOSE: Aggregate performance by role/persona (from campaign_metrics.roles_snapshot); expose get_persona_scores() for lead scoring
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PERSONA_CACHE_KEY = "campaign_learning:persona_scores"
PERSONA_CACHE_TTL = 3600  ***REMOVED*** 1h


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def get_persona_scores() -> Dict[str, float]:
    """Return dict role -> score (0..1) for persona effectiveness. Cached in Redis when available."""
    redis = _get_redis()
    if redis:
        try:
            raw = redis.get(PERSONA_CACHE_KEY)
            if raw:
                import json
                return json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            pass
    try:
        from src.db.base import SessionLocal
        from src.learning.models.campaign_metrics import CampaignMetrics
        db = SessionLocal()
        try:
            rows = db.query(CampaignMetrics).filter(CampaignMetrics.roles_snapshot.isnot(None)).limit(2000).all()
        finally:
            db.close()
    except Exception as e:
        logger.debug("get_persona_scores: %s", e)
        return {}
    role_agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        try:
            roles = json.loads(r.roles_snapshot) if isinstance(r.roles_snapshot, str) else r.roles_snapshot
            if not isinstance(roles, list):
                roles = [r.roles_snapshot] if r.roles_snapshot else []
            sent = max(1, r.emails_sent or 0)
            reply_rate = (r.replies_received or 0) / sent
            for role in roles:
                role = (role or "").strip() or "_unknown"
                role_agg.setdefault(role, {"sent": 0, "replies": 0})
                role_agg[role]["sent"] += r.emails_sent or 0
                role_agg[role]["replies"] += r.replies_received or 0
        except Exception:
            continue
    scores = {}
    for role, s in role_agg.items():
        sent = max(1, s["sent"])
        scores[role] = round(s["replies"] / sent, 4)
    if redis and scores:
        try:
            redis.setex(PERSONA_CACHE_KEY, PERSONA_CACHE_TTL, json.dumps(scores))
        except Exception:
            pass
    return scores


def refresh_persona_performance(db_session: Any = None) -> Dict[str, Any]:
    """Recompute persona scores from campaign_metrics and cache. No separate table; in-memory/Redis only."""
    get_persona_scores()
    return {"ok": True}
