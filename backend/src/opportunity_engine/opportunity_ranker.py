"""
OPPORTUNITY_ENGINE: opportunity_ranker
PURPOSE: Score 0.0-1.0 from industry reply, persona success, company similarity, market signals, campaign engagement.
Select best target persona (CEO, CTO, Founder, VP Operations, Procurement Director) with confidence.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from src.opportunity_engine.models.opportunity import Opportunity
from src.opportunity_engine.models.opportunity_score import OpportunityScore

logger = logging.getLogger(__name__)

TARGET_PERSONAS = ["CEO", "CTO", "Founder", "VP Operations", "Procurement Director"]


def rank_opportunities(
    opportunities: List[Opportunity],
    limit: int = 50,
    industry_rates: Optional[Dict[str, float]] = None,
    persona_scores: Optional[Dict[str, float]] = None,
    market_signal_strength: Optional[float] = None,
) -> List[OpportunityScore]:
    """
    Score each opportunity 0.0-1.0 using:
    industry reply performance, persona success rates, company similarity, recent market signals, campaign engagement.
    Then assign recommended_persona and confidence.
    """
    if industry_rates is None or persona_scores is None:
        try:
            from src.campaign_learning.industry_performance_model import get_industry_rates
            from src.campaign_learning.persona_performance_model import get_persona_scores
            industry_rates = industry_rates or get_industry_rates()
            persona_scores = persona_scores or get_persona_scores()
        except Exception:
            industry_rates = industry_rates or {}
            persona_scores = persona_scores or {}
    scored: List[OpportunityScore] = []
    for opp in opportunities:
        breakdown, total = _compute_score_breakdown(
            opp,
            industry_rates=industry_rates,
            persona_scores=persona_scores,
            market_signal_strength=market_signal_strength,
        )
        persona, confidence = _select_best_persona(opp, persona_scores)
        score_val = round(min(1.0, total), 4)
        signals_list = opp.signals or []
        scored.append(OpportunityScore(
            company=opp.company,
            company_id=opp.company_id,
            industry=opp.industry,
            region=opp.region,
            score=score_val,
            recommended_persona=persona,
            confidence=round(confidence, 4),
            signals=opp.signals,
            score_breakdown=breakdown,
        ))
        ***REMOVED*** Anomaly: score > 0.95 with fewer than 1 signal (logged for monitoring/log_ingestor)
        if score_val > 0.95 and len(signals_list) < 1:
            logger.warning(
                "opportunity_scoring_anomaly: score=%.2f signals_count=%s company=%s company_id=%s",
                score_val, len(signals_list), opp.company, opp.company_id,
            )
    scored.sort(key=lambda x: -x.score)
    return scored[:limit]


def _compute_score_breakdown(
    opp: Opportunity,
    industry_rates: Dict[str, float],
    persona_scores: Dict[str, float],
    market_signal_strength: Optional[float] = None,
) -> Tuple[Dict[str, float], float]:
    """Weights: industry_reply 0.25, persona_success 0.25, similarity 0.2, market_signals 0.15, engagement 0.15."""
    w = {
        "industry_reply": 0.25,
        "persona_success": 0.25,
        "similarity": 0.2,
        "market_signals": 0.15,
        "engagement": 0.15,
    }
    breakdown = {}
    ind = opp.industry or ""
    industry_reply = float(industry_rates.get(ind, 0.5))
    breakdown["industry_reply"] = industry_reply
    persona_success = 0.5
    if persona_scores:
        persona_success = sum(persona_scores.values()) / max(len(persona_scores), 1)
    breakdown["persona_success"] = min(1.0, persona_success)
    similarity = 0.5
    if "similar_company_response" in (opp.signals or []):
        similarity = 0.85
    breakdown["similarity"] = similarity
    if market_signal_strength is not None:
        market_signals = market_signal_strength
    else:
        try:
            from src.market_signals.signal_weights import get_signal_weights
            weights = get_signal_weights()
            sig_list = opp.signals or []
            if sig_list:
                market_signals = sum(weights.get(s, 0.6) for s in sig_list) / len(sig_list)
                market_signals = min(1.0, market_signals)
            else:
                market_signals = 0.3
        except Exception:
            market_signals = 0.7 if (opp.signals or []) else 0.3
    breakdown["market_signals"] = market_signals
    engagement = 0.6 if any(s in (opp.signals or []) for s in ("geographic_engagement_cluster", "industry_reply_rate_increase")) else 0.4
    breakdown["engagement"] = engagement
    total = (
        industry_reply * w["industry_reply"]
        + breakdown["persona_success"] * w["persona_success"]
        + similarity * w["similarity"]
        + market_signals * w["market_signals"]
        + engagement * w["engagement"]
    )
    return breakdown, total


def _select_best_persona(opp: Opportunity, persona_scores: Dict[str, float]) -> Tuple[str, float]:
    """Best target role from TARGET_PERSONAS and historical performance; return (role, confidence)."""
    if not persona_scores:
        return ("VP Operations", 0.5)
    best_role = "VP Operations"
    best_score = 0.0
    for role in TARGET_PERSONAS:
        s = float(persona_scores.get(role, 0.5))
        if s > best_score:
            best_score = s
            best_role = role
    confidence = min(1.0, 0.5 + best_score * 0.5)
    return (best_role, confidence)
