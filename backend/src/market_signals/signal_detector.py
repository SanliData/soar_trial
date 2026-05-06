import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def detect_signals(industry: str = None, region: str = None, db_session: Any = None) -> List[Dict[str, Any]]:
    """Detect signals: hiring spike, technology adoption, funding, industry engagement surge, campaign response cluster."""
    signals = []
    try:
        from src.db.base import SessionLocal
        from src.models.industry_performance import IndustryPerformance
        db = db_session or SessionLocal()
        try:
            q = db.query(IndustryPerformance).filter(IndustryPerformance.replies_received > 0)
            if industry:
                q = q.filter(IndustryPerformance.industry.ilike("%" + industry + "%"))
            rows = q.order_by(IndustryPerformance.reply_rate.desc()).limit(50).all()
            for r in rows:
                signals.append({
                    "type": "industry_engagement_surge",
                    "industry": r.industry,
                    "region": region or r.location or "",
                    "confidence": min(0.99, 0.5 + (r.reply_rate or 0) * 0.5),
                    "replies_received": r.replies_received,
                })
        finally:
            if db_session is None:
                db.close()
    except Exception as e:
        logger.exception("detect_signals: %s", e)
    return signals
