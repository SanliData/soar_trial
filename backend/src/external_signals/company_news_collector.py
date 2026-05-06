"""
EXTERNAL_SIGNALS: Company news collector
PURPOSE: Collect technology adoption and company expansion signals from news (stub + Redis)
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SIGNAL_TYPE_TECHNOLOGY_ADOPTION = "technology_adoption"
SIGNAL_TYPE_COMPANY_EXPANSION = "company_expansion"


def _store(signal: Dict[str, Any]) -> None:
    try:
        from src.market_signals.signal_store import store_signal
        store_signal(signal)
    except Exception as e:
        logger.debug("company_news_collector store: %s", e)


def collect_company_news_signals(
    company_id: int = None,
    company_name: str = None,
    industry: str = None,
    region: str = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Collect technology adoption and company expansion signals from news. Store in Redis.
    """
    signals: List[Dict[str, Any]] = []
    try:
        ***REMOVED*** Placeholder: integrate with news API or RSS
        for sig_type in (SIGNAL_TYPE_TECHNOLOGY_ADOPTION, SIGNAL_TYPE_COMPANY_EXPANSION):
            sig = {
                "type": sig_type,
                "source": "company_news",
                "company_id": company_id,
                "company_name": company_name or "",
                "industry": industry or "",
                "region": region or "",
                "confidence": 0.65,
            }
            _store(sig)
            signals.append(sig)
    except Exception as e:
        logger.warning("collect_company_news_signals: %s", e)
    return signals[:limit]
