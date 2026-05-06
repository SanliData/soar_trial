"""
CAMPAIGN_LEARNING: message_performance_analyzer
PURPOSE: Analyze message/email style performance (subject, opened, replied)
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def analyze_message_performance(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate email_performance rows: by subject length, by campaign, overall open/reply rates.
    rows: list of dicts with keys e.g. subject, opened, replied, positive, campaign_id.
    """
    total_sent = 0
    total_opened = 0
    total_replied = 0
    by_campaign: Dict[str, Dict[str, int]] = {}
    subject_length_buckets: Dict[str, Dict[str, int]] = {"short": {"sent": 0, "replied": 0}, "medium": {"sent": 0, "replied": 0}, "long": {"sent": 0, "replied": 0}}
    for r in rows:
        total_sent += 1
        total_opened += (r.get("opened") or 0) or (1 if r.get("opened") else 0)
        total_replied += (r.get("replied") or 0) or (1 if r.get("replied") else 0)
        cid = r.get("campaign_id") or "_unknown"
        by_campaign.setdefault(cid, {"sent": 0, "opened": 0, "replied": 0})
        by_campaign[cid]["sent"] += 1
        by_campaign[cid]["opened"] += (r.get("opened") or 0) or 0
        by_campaign[cid]["replied"] += (r.get("replied") or 0) or 0
        subj = (r.get("subject") or "")[:200]
        length = "short" if len(subj) < 40 else ("long" if len(subj) > 80 else "medium")
        subject_length_buckets[length]["sent"] += 1
        if r.get("replied"):
            subject_length_buckets[length]["replied"] += 1
    return {
        "total_sent": total_sent,
        "total_opened": total_opened,
        "total_replied": total_replied,
        "open_rate": round(total_opened / max(1, total_sent), 4),
        "reply_rate": round(total_replied / max(1, total_sent), 4),
        "by_campaign": by_campaign,
        "subject_length_performance": subject_length_buckets,
    }
