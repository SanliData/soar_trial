import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def schedule_outreach(contact_id: str, sequence: List[Dict[str, Any]], delay_minutes: int = 0) -> Dict[str, Any]:
    try:
        from src.core.cache import get_redis_client
        r = get_redis_client()
        if r:
            import json
            r.setex("automation:schedule:%s" % contact_id, 86400 * 30, json.dumps({"sequence": sequence}))
            return {"ok": True, "contact_id": contact_id}
    except Exception as e:
        logger.exception("schedule_outreach: %s", e)
    return {"ok": False}
