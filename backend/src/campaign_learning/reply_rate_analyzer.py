# reply_rate_analyzer: compute reply/open rates from campaign metrics
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def compute_reply_rates(
    emails_sent: int,
    emails_opened: int = 0,
    replies_received: int = 0,
    positive_responses: int = 0,
) -> Dict[str, float]:
    sent = max(1, emails_sent)
    return {
        "open_rate": round((emails_opened or 0) / sent, 4),
        "reply_rate": round((replies_received or 0) / sent, 4),
        "positive_rate": round((positive_responses or 0) / sent, 4),
    }


def aggregate_reply_rates_by_dimension(
    rows: List[Dict[str, Any]],
    dimension_key: str,
    sent_key: str = "emails_sent",
    opened_key: str = "emails_opened",
    replies_key: str = "replies_received",
    positive_key: str = "positive_responses",
) -> Dict[str, Dict[str, Any]]:
    agg: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        dim = r.get(dimension_key) or "_unknown"
        if dim not in agg:
            agg[dim] = {"sent": 0, "opened": 0, "replies": 0, "positive": 0}
        agg[dim]["sent"] += r.get(sent_key) or 0
        agg[dim]["opened"] += r.get(opened_key) or 0
        agg[dim]["replies"] += r.get(replies_key) or 0
        agg[dim]["positive"] += r.get(positive_key) or 0
    for dim, s in agg.items():
        sent = max(1, s["sent"])
        s["open_rate"] = round(s["opened"] / sent, 4)
        s["reply_rate"] = round(s["replies"] / sent, 4)
        s["positive_rate"] = round(s["positive"] / sent, 4)
    return agg
