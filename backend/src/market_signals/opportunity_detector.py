import logging
from typing import Any, Dict, List

from src.market_signals.signal_detector import detect_signals
from src.market_signals.signal_store import get_signals

logger = logging.getLogger(__name__)


def detect_opportunities(industry: str = None, region: str = None) -> List[Dict[str, Any]]:
    """Combine live detection and stored signals into opportunity list."""
    opportunities = []
    live = detect_signals(industry=industry, region=region)
    stored = get_signals(industry=industry, region=region, limit=30)
    seen = set()
    for s in live + stored:
        key = (s.get("type"), s.get("industry"), s.get("region"))
        if key in seen:
            continue
        seen.add(key)
        opportunities.append(s)
    return opportunities[:50]
