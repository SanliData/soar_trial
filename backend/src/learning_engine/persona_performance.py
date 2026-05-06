import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_persona_metrics() -> Dict[str, Any]:
    """reply_rate_by_persona from campaign metrics."""
    try:
        from src.campaign_learning.persona_performance_model import get_persona_scores
        return get_persona_scores()
    except Exception as e:
        logger.debug("get_persona_metrics: %s", e)
    return {}
