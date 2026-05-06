"""
EXTERNAL_SIGNALS: Funding signal collector
PURPOSE: Collect funding event signals (stub + Redis for market_signals engine)
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SIGNAL_TYPE_FUNDING_EVENT = "funding_event"


def _store(signal: Dict[str, Any]) -> None:
    try:
        from src.market_signals.signal_store import store_signal
        store_signal(signal)
    except Exception as e:
        logger.debug("funding_signal_collector store: %s", e)


def collect_funding_signals(
    industry: str = None,
    region: str = None,
    company_id: int = None,
    company_name: str = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Collect funding event signals. Store in Redis; consumed by market_signals engine.
    """
    signals: List[Dict[str, Any]] = []
    try:
        # Placeholder: integrate with Crunchbase/API or DB of funding rounds
        sig = {
            "type": SIGNAL_TYPE_FUNDING_EVENT,
            "source": "funding",
            "industry": industry or "",
            "region": region or "",
            "company_id": company_id,
            "company_name": company_name or "",
            "confidence": 0.75,
        }
        _store(sig)
        signals.append(sig)
    except Exception as e:
        logger.warning("collect_funding_signals: %s", e)
    return signals[:limit]
