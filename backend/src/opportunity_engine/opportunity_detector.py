"""
OPPORTUNITY_ENGINE: opportunity_detector
PURPOSE: Identify candidate opportunities from Company Graph, Market Signals, Learning Engine, Campaign DB.
Signals: hiring_spike, similar_company_response, industry_reply_rate_increase, geographic_engagement_cluster.
"""
import logging
from typing import Any, Dict, List, Optional

from src.opportunity_engine.models.opportunity import Opportunity

logger = logging.getLogger(__name__)

SIGNAL_HIRING_SPIKE = "hiring_spike"
SIGNAL_SIMILAR_COMPANY_RESPONSE = "similar_company_response"
SIGNAL_INDUSTRY_REPLY_RATE_INCREASE = "industry_reply_rate_increase"
SIGNAL_GEOGRAPHIC_ENGAGEMENT_CLUSTER = "geographic_engagement_cluster"


def detect_opportunities(
    industry: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
    db_session: Any = None,
) -> List[Opportunity]:
    """
    Return candidate opportunities: company, industry, region, signals[].
    Integrates Company Graph, Market Signals, Learning Engine, Campaign DB.
    """
    candidates: List[Opportunity] = []
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception as e:
            logger.debug("detect_opportunities: no db %s", e)
            return []
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        from src.models.industry_performance import IndustryPerformance
        from src.learning.models.campaign_metrics import CampaignMetrics
        industry_high_reply = set()
        geo_engagement = set()
        try:
            for r in db.query(IndustryPerformance).filter(IndustryPerformance.reply_rate.isnot(None)).filter(IndustryPerformance.reply_rate > 0.1).limit(100).all():
                industry_high_reply.add((r.industry or "").strip())
        except Exception:
            pass
        try:
            for r in db.query(CampaignMetrics).filter(CampaignMetrics.replies_received > 0).limit(200).all():
                if r.location:
                    geo_engagement.add((r.location or "").strip())
                if r.industry:
                    industry_high_reply.add((r.industry or "").strip())
        except Exception:
            pass
        market_signal_list: List[Dict[str, Any]] = []
        try:
            from src.market_signals.signal_detector import detect_signals
            market_signal_list = detect_signals(industry=industry, region=region)
        except Exception:
            pass
        similar_company_ids = set()
        try:
            from src.company_graph.similarity_engine import find_similar_companies
            for c in db.query(IntelCompany).filter(IntelCompany.industry.isnot(None)).limit(20).all():
                sim = find_similar_companies(company_id=c.id, limit=5)
                for s in (sim.get("similar_companies") or []):
                    if isinstance(s, dict) and s.get("name"):
                        similar_company_ids.add(s["name"])
        except Exception:
            pass
        q = db.query(IntelCompany)
        if industry:
            q = q.filter(IntelCompany.industry.ilike("%" + industry + "%"))
        if region:
            q = q.filter(IntelCompany.location.ilike("%" + region + "%"))
        q = q.limit(limit * 2)
        seen = set()
        for c in q.all():
            name = (c.company_name or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            ind = (c.industry or "").strip()
            loc = (c.location or "").strip()
            signals: List[str] = []
            if ind in industry_high_reply:
                signals.append(SIGNAL_INDUSTRY_REPLY_RATE_INCREASE)
            if loc and loc in geo_engagement:
                signals.append(SIGNAL_GEOGRAPHIC_ENGAGEMENT_CLUSTER)
            if name in similar_company_ids or market_signal_list:
                signals.append(SIGNAL_SIMILAR_COMPANY_RESPONSE)
            if market_signal_list and (ind or loc):
                for ms in market_signal_list:
                    if (ms.get("type") or "").lower().find("hiring") >= 0:
                        signals.append(SIGNAL_HIRING_SPIKE)
                        break
            if not signals:
                signals.append(SIGNAL_SIMILAR_COMPANY_RESPONSE)
            candidates.append(Opportunity(
                company=name,
                company_id=c.id,
                industry=ind or None,
                region=loc or None,
                signals=list(dict.fromkeys(signals)),
                properties={"technologies": c.technologies},
            ))
        return candidates[:limit]
    except Exception as e:
        logger.exception("detect_opportunities: %s", e)
        return []
    finally:
        if close and db:
            db.close()
