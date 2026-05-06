import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def analyze_campaigns(limit: int = 100) -> Dict[str, Any]:
    try:
        from src.db.base import SessionLocal
        from src.learning.models.campaign_metrics import CampaignMetrics
        db = SessionLocal()
        rows = db.query(CampaignMetrics).limit(limit).all()
        db.close()
        out = [{"campaign_id": r.campaign_id, "reply_rate": (r.replies_received or 0) / max(1, r.emails_sent or 0)} for r in rows]
        return {"campaigns": out, "count": len(out)}
    except Exception as e:
        logger.exception("analyze_campaigns: %s", e)
    return {"campaigns": [], "count": 0}
