"""
EXPERIMENT_ENGINE: experiment_manager
PURPOSE: Register and retrieve A/B experiments (email templates, subject lines, persona targeting, message tone)
"""
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

EXPERIMENT_TYPES = ("email_template", "subject_line", "persona_targeting", "message_tone")
REDIS_KEY_PREFIX = "experiment_engine:experiments"
REDIS_KEY_INDEX = "experiment_engine:experiment_index"
REDIS_TTL = 86400 * 30   # 30 days


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def register_experiment(
    experiment_id: str,
    experiment_type: str,
    variants: List[Dict[str, Any]],
    traffic_split: Optional[Dict[str, float]] = None,
) -> bool:
    """
    Register an A/B experiment. experiment_type: email_template | subject_line | persona_targeting | message_tone.
    variants: list of { "id": "A", "config": {...} }. traffic_split: optional {"A": 0.5, "B": 0.5}.
    """
    if experiment_type not in EXPERIMENT_TYPES:
        logger.warning("experiment_manager: unknown type %s", experiment_type)
        return False
    r = _redis()
    if not r:
        return False
    if not traffic_split and variants:
        traffic_split = {v["id"]: 1.0 / len(variants) for v in variants}
    payload = {
        "experiment_id": experiment_id,
        "experiment_type": experiment_type,
        "variants": variants,
        "traffic_split": traffic_split or {},
    }
    try:
        key = f"{REDIS_KEY_PREFIX}:{experiment_id}"
        r.setex(key, REDIS_TTL, json.dumps(payload))
        r.sadd(REDIS_KEY_INDEX, experiment_id)
        return True
    except Exception as e:
        logger.debug("register_experiment: %s", e)
        return False


def get_experiment(experiment_id: str) -> Optional[Dict[str, Any]]:
    """Get experiment by id from Redis."""
    r = _redis()
    if not r:
        return None
    try:
        raw = r.get(f"{REDIS_KEY_PREFIX}:{experiment_id}")
        if not raw:
            return None
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception as e:
        logger.debug("get_experiment: %s", e)
        return None


def list_experiments(experiment_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all experiments, optionally filtered by type."""
    r = _redis()
    if not r:
        return []
    try:
        ids = list(r.smembers(REDIS_KEY_INDEX) or [])
        out = []
        for eid in ids:
            sid = eid.decode() if isinstance(eid, bytes) else eid
            ex = get_experiment(sid)
            if ex and (experiment_type is None or ex.get("experiment_type") == experiment_type):
                out.append(ex)
        return out
    except Exception as e:
        logger.debug("list_experiments: %s", e)
        return []
