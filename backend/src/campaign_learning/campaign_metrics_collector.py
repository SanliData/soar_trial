***REMOVED*** campaign_metrics_collector: collect campaign outcomes and persist to campaign_metrics
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def collect_campaign_metrics(
    campaign_id: str,
    emails_sent: int,
    emails_opened: int = 0,
    replies_received: int = 0,
    positive_responses: int = 0,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    roles_snapshot: Optional[List[str]] = None,
    db_session: Optional[Any] = None,
) -> Dict[str, Any]:
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception as e:
            logger.warning("campaign_metrics_collector: no db: %s", e)
            return {"ok": False, "error": str(e)}
    else:
        db = db_session
    try:
        from src.learning.models.campaign_metrics import CampaignMetrics
        existing = db.query(CampaignMetrics).filter(CampaignMetrics.campaign_id == campaign_id).first()
        roles_str = json.dumps(roles_snapshot) if roles_snapshot else None
        if existing:
            existing.emails_sent = emails_sent
            existing.emails_opened = emails_opened
            existing.replies_received = replies_received
            existing.positive_responses = positive_responses
            if industry is not None:
                existing.industry = industry
            if location is not None:
                existing.location = location
            if roles_snapshot is not None:
                existing.roles_snapshot = roles_str
            db.commit()
            return {"ok": True, "updated": True, "campaign_id": campaign_id}
        m = CampaignMetrics(
            campaign_id=campaign_id,
            emails_sent=emails_sent,
            emails_opened=emails_opened,
            replies_received=replies_received,
            positive_responses=positive_responses,
            industry=industry,
            location=location,
            roles_snapshot=roles_str,
        )
        db.add(m)
        db.commit()
        return {"ok": True, "created": True, "campaign_id": campaign_id}
    except Exception as e:
        logger.exception("campaign_metrics_collector: %s", e)
        if db_session is None and db:
            db.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        if close and db:
            db.close()
