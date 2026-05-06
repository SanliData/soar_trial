"""
EXTERNAL_SIGNALS: Job posting signal collector
PURPOSE: Collect hiring spike signals from job postings (stub + Redis)
"""
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SIGNAL_TYPE_HIRING_SPIKE = "hiring_spike"


def _store(signal: Dict[str, Any]) -> None:
    try:
        from src.market_signals.signal_store import store_signal
        store_signal(signal)
    except Exception as e:
        logger.debug("job_posting_signal_collector store: %s", e)


def collect_job_posting_signals(
    company_id: int = None,
    company_name: str = None,
    industry: str = None,
    region: str = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Collect hiring spike signals from job postings. Store in Redis for market_signals engine.
    """
    signals: List[Dict[str, Any]] = []
    try:
        # Placeholder: integrate with job boards / LinkedIn jobs API
        sig = {
            "type": SIGNAL_TYPE_HIRING_SPIKE,
            "source": "job_posting",
            "company_id": company_id,
            "company_name": company_name or "",
            "industry": industry or "",
            "region": region or "",
            "confidence": 0.8,
        }
        _store(sig)
        signals.append(sig)
    except Exception as e:
        logger.warning("collect_job_posting_signals: %s", e)
    return signals[:limit]
