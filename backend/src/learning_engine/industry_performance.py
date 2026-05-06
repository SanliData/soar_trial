import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_industry_metrics() -> Dict[str, Any]:
    """reply_rate_by_industry, time_of_day_performance (placeholder)."""
    try:
        from src.campaign_learning.industry_performance_model import get_industry_rates
        return get_industry_rates()
    except Exception as e:
        logger.debug("get_industry_metrics: %s", e)
    return {}
