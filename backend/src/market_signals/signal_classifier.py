import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def classify_signal(signal: Dict[str, Any]) -> str:
    """Classify signal type: hiring_spike, technology_adoption, funding_event, industry_engagement_surge, campaign_response_cluster."""
    t = (signal.get("type") or "").lower()
    if "hiring" in t or "hire" in str(signal):
        return "hiring_spike"
    if "tech" in t or "technology" in t:
        return "technology_adoption"
    if "funding" in t or "fund" in t:
        return "funding_event"
    if "industry" in t or "engagement" in t:
        return "industry_engagement_surge"
    if "campaign" in t or "response" in t:
        return "campaign_response_cluster"
    return "unknown"
