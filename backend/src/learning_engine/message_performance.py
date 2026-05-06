import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_message_metrics(limit: int = 500) -> Dict[str, Any]:
    """message_success_score, subject performance from email_performance."""
    try:
        from src.db.base import SessionLocal
        from src.models.email_performance import EmailPerformance
        db = SessionLocal()
        try:
            rows = db.query(EmailPerformance).limit(limit).all()
            replied = sum(1 for r in rows if r.replied)
            total = max(1, len(rows))
            return {"message_success_score": replied / total, "total_emails": total, "replied": replied}
        finally:
            db.close()
    except Exception as e:
        logger.debug("get_message_metrics: %s", e)
    return {"message_success_score": 0, "total_emails": 0, "replied": 0}
