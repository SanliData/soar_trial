"""
CAMPAIGN_LEARNING: industry_performance_model
PURPOSE: Read/write industry-level performance; persist to industry_performance table
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_industry_rates() -> Dict[str, float]:
    """Return dict industry -> reply_rate from industry_performance table."""
    try:
        from src.db.base import SessionLocal
        from src.models.industry_performance import IndustryPerformance
        db = SessionLocal()
        try:
            rows = db.query(IndustryPerformance.industry, IndustryPerformance.reply_rate).filter(
                IndustryPerformance.reply_rate.isnot(None)
            ).all()
            return {r[0]: float(r[1]) for r in rows}
        finally:
            db.close()
    except Exception as e:
        logger.debug("get_industry_rates: %s", e)
    return {}


def refresh_industry_performance(period_days: int = 90, db_session: Any = None) -> Dict[str, Any]:
    """Aggregate campaign_metrics by industry and upsert into industry_performance."""
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception as e:
            return {"ok": False, "error": str(e)}
    else:
        db = db_session
    try:
        from src.learning.models.campaign_metrics import CampaignMetrics
        from src.models.industry_performance import IndustryPerformance
        since = datetime.utcnow() - timedelta(days=period_days)
        rows = db.query(CampaignMetrics).filter(CampaignMetrics.created_at >= since).filter(
            CampaignMetrics.industry.isnot(None)
        ).all()
        agg: Dict[tuple, Dict[str, Any]] = {}
        for r in rows:
            ind = (r.industry or "").strip() or "_unknown"
            loc = (r.location or "").strip() or None
            key = (ind, loc)
            if key not in agg:
                agg[key] = {"sent": 0, "opened": 0, "replies": 0, "positive": 0}
            agg[key]["sent"] += r.emails_sent or 0
            agg[key]["opened"] += r.emails_opened or 0
            agg[key]["replies"] += r.replies_received or 0
            agg[key]["positive"] += r.positive_responses or 0
        period_end = date.today()
        period_start = period_end - timedelta(days=period_days)
        for (industry, location), s in agg.items():
            sent = max(1, s["sent"])
            open_rate = s["opened"] / sent
            reply_rate = s["replies"] / sent
            existing = db.query(IndustryPerformance).filter(
                IndustryPerformance.industry == industry,
            ).filter(
                IndustryPerformance.location == location if location else IndustryPerformance.location.is_(None)
            ).first()
            if existing:
                existing.emails_sent = s["sent"]
                existing.emails_opened = s["opened"]
                existing.replies_received = s["replies"]
                existing.positive_responses = s["positive"]
                existing.open_rate = open_rate
                existing.reply_rate = reply_rate
                existing.period_start = period_start
                existing.period_end = period_end
            else:
                db.add(IndustryPerformance(
                    industry=industry,
                    location=location,
                    emails_sent=s["sent"],
                    emails_opened=s["opened"],
                    replies_received=s["replies"],
                    positive_responses=s["positive"],
                    open_rate=open_rate,
                    reply_rate=reply_rate,
                    period_start=period_start,
                    period_end=period_end,
                ))
        db.commit()
        return {"ok": True, "rows_upserted": len(agg)}
    except Exception as e:
        logger.exception("refresh_industry_performance: %s", e)
        if db_session is None and db:
            db.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        if close and db:
            db.close()
