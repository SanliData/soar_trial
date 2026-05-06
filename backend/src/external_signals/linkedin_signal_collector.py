"""
EXTERNAL_SIGNALS: LinkedIn signal collector
PURPOSE: Collect hiring spike and company expansion signals from LinkedIn (stub + Redis)
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SIGNAL_TYPE_HIRING_SPIKE = "hiring_spike"
SIGNAL_TYPE_COMPANY_EXPANSION = "company_expansion"


def _store(signal: Dict[str, Any]) -> None:
    try:
        from src.market_signals.signal_store import store_signal
        store_signal(signal)
    except Exception as e:
        logger.debug("linkedin_signal_collector store: %s", e)


def collect_linkedin_signals(
    company_id: int = None,
    company_name: str = None,
    industry: str = None,
    region: str = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Collect LinkedIn-derived signals (hiring spike, company expansion).
    Stores each signal in Redis for market_signals engine. Returns list of stored signals.
    """
    signals: List[Dict[str, Any]] = []
    try:
        ***REMOVED*** Placeholder: in production integrate with LinkedIn API or scraped data
        ***REMOVED*** Example: hiring spike when job count increase detected for company/industry
        if industry or region:
            sig = {
                "type": SIGNAL_TYPE_HIRING_SPIKE,
                "source": "linkedin",
                "industry": industry or "",
                "region": region or "",
                "company_id": company_id,
                "company_name": company_name or "",
                "confidence": 0.7,
            }
            _store(sig)
            signals.append(sig)
        if company_id or company_name:
            sig_exp = {
                "type": SIGNAL_TYPE_COMPANY_EXPANSION,
                "source": "linkedin",
                "company_id": company_id,
                "company_name": company_name or "",
                "industry": industry or "",
                "region": region or "",
                "confidence": 0.6,
            }
            _store(sig_exp)
            signals.append(sig_exp)
    except Exception as e:
        logger.warning("collect_linkedin_signals: %s", e)
    return signals[:limit]
