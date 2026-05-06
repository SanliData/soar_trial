import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from src.market_signals.signal_detector import detect_signals
from src.market_signals.signal_store import get_signals
from src.market_signals.signal_weights import get_signal_weights, set_signal_weights

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/signals", tags=["market-signals"])


@router.get("/weights")
async def get_signal_weights_endpoint() -> Dict[str, float]:
    """GET /v1/signals/weights — current signal weights used by opportunity scoring (runtime)."""
    return get_signal_weights()


class SignalWeightsUpdate(BaseModel):
    weights: Dict[str, float] = Field(..., description="e.g. {\"hiring_spike\": 0.6, \"funding_event\": 0.8}")


@router.put("/weights")
async def put_signal_weights_endpoint(body: SignalWeightsUpdate) -> Dict[str, float]:
    """PUT /v1/signals/weights — update signal weights at runtime (persisted in Redis)."""
    if set_signal_weights(body.weights):
        return get_signal_weights()
    return get_signal_weights()


@router.get("/industry")
async def signals_by_industry(industry: str = Query(None)) -> dict:
    """GET /signals/industry?industry=fiber+infrastructure."""
    signals = detect_signals(industry=industry) if industry else []
    stored = get_signals(industry=industry, limit=30)
    return {"signals": signals[:20], "stored": stored[:20]}


@router.get("/region")
async def signals_by_region(region: str = Query(None)) -> dict:
    """GET /signals/region?region=Texas."""
    signals = detect_signals(region=region) if region else []
    stored = get_signals(region=region, limit=30)
    return {"signals": signals[:20], "stored": stored[:20]}
