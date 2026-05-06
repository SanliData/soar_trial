"""
OPPORTUNITY_ENGINE: opportunity_explain
PURPOSE: Explain opportunity score for a single company (score breakdown + signals)
"""
import logging
from typing import Any, Dict, List, Optional

from src.opportunity_engine.models.opportunity import Opportunity
from src.opportunity_engine.models.opportunity_score import OpportunityScore
from src.opportunity_engine.opportunity_detector import (
    detect_opportunities,
    SIGNAL_HIRING_SPIKE,
    SIGNAL_SIMILAR_COMPANY_RESPONSE,
)
from src.opportunity_engine.opportunity_ranker import rank_opportunities

logger = logging.getLogger(__name__)


def _breakdown_to_explain(score_breakdown: Dict[str, float]) -> Dict[str, float]:
    """Map internal breakdown keys to explain API keys."""
    return {
        "industry_performance": round(score_breakdown.get("industry_reply", 0.5), 2),
        "persona_success": round(score_breakdown.get("persona_success", 0.5), 2),
        "market_signals": round(score_breakdown.get("market_signals", 0.5), 2),
        "company_similarity": round(score_breakdown.get("similarity", 0.5), 2),
    }


def explain_opportunity(
    company_id: int,
    db_session: Any = None,
) -> Optional[Dict[str, Any]]:
    """
    Get score explanation for a company by id.
    Returns dict with company, score, score_breakdown (industry_performance, persona_success, market_signals, company_similarity), signals.
    """
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception as e:
            logger.debug("explain_opportunity: no db %s", e)
            return None
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        c = db.query(IntelCompany).filter(IntelCompany.id == company_id).first()
        if not c:
            return None
        name = (c.company_name or "").strip() or f"Company_{company_id}"
        industry = (c.industry or "").strip()
        region = (c.location or "").strip()
        signals: List[str] = []
        try:
            cands = detect_opportunities(industry=industry or None, region=region or None, limit=50, db_session=db)
            for cand in cands:
                if cand.company_id == company_id or (cand.company or "").strip() == name:
                    signals = list(cand.signals or [])
                    break
        except Exception:
            pass
        if not signals:
            signals = [SIGNAL_SIMILAR_COMPANY_RESPONSE]
        opp = Opportunity(
            company=name,
            company_id=company_id,
            industry=industry or None,
            region=region or None,
            signals=signals,
            properties={},
        )
        scored_list: List[OpportunityScore] = rank_opportunities([opp], limit=1)
        if not scored_list:
            return {
                "company": name,
                "score": 0.5,
                "score_breakdown": {
                    "industry_performance": 0.5,
                    "persona_success": 0.5,
                    "market_signals": 0.5,
                    "company_similarity": 0.5,
                },
                "signals": signals,
            }
        s = scored_list[0]
        return {
            "company": s.company,
            "score": round(s.score, 2),
            "score_breakdown": _breakdown_to_explain(s.score_breakdown or {}),
            "signals": list(s.signals or []),
        }
    except Exception as e:
        logger.exception("explain_opportunity: %s", e)
        return None
    finally:
        if close and db:
            db.close()
