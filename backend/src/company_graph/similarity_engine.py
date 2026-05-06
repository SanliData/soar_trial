"""
COMPANY_GRAPH: similarity_engine
PURPOSE: Compute company similarity by industry, size, technology stack, campaign engagement
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def find_similar_companies(
    company_id: Optional[int] = None,
    company_name: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = 10,
    db_session: Any = None,
) -> Dict[str, Any]:
    """
    Return { "company": "<name>", "similar_companies": [ {"name": "...", "score": 0.86}, ... ] }.
    Uses industry, location, technologies; optional embeddings for semantic similarity.
    """
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception:
            return {"company": company_name or "Unknown", "similar_companies": []}
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        ref = None
        if company_id:
            ref = db.query(IntelCompany).filter(IntelCompany.id == company_id).first()
        if ref:
            company_name = ref.company_name
            industry = industry or ref.industry
            location = getattr(ref, "location", None)
            tech = ref.technologies or []
        else:
            location = None
            tech = []
        candidates = db.query(IntelCompany).filter(IntelCompany.id != (ref.id if ref else -1)).limit(500).all()
        scored: List[tuple] = []
        for c in candidates:
            s = _score_similarity(
                ref_industry=industry,
                ref_location=location,
                ref_tech=tech if isinstance(tech, list) else [],
                c_industry=c.industry,
                c_location=c.location,
                c_tech=c.technologies or [],
            )
            if s > 0:
                scored.append((s, c.company_name))
        scored.sort(key=lambda x: -x[0])
        similar = [{"name": name, "score": round(score, 2)} for score, name in scored[:limit]]
        return {"company": company_name or "Unknown", "similar_companies": similar}
    except Exception as e:
        logger.exception("similarity_engine: %s", e)
        return {"company": company_name or "Unknown", "similar_companies": []}
    finally:
        if close and db:
            db.close()


def _score_similarity(
    ref_industry: Optional[str],
    ref_location: Optional[str],
    ref_tech: List[Any],
    c_industry: Optional[str],
    c_location: Optional[str],
    c_tech: List[Any],
) -> float:
    """Heuristic similarity 0..1 from industry, location, tech overlap."""
    score = 0.0
    if ref_industry and c_industry:
        if ref_industry.lower() == c_industry.lower():
            score += 0.5
        elif ref_industry.lower() in c_industry.lower() or c_industry.lower() in ref_industry.lower():
            score += 0.3
    if ref_location and c_location and str(ref_location).lower() == str(c_location).lower():
        score += 0.2
    rset = set(str(t).lower() for t in ref_tech[:20])
    cset = set(str(t).lower() for t in (c_tech or [])[:20])
    if rset and cset:
        score += 0.3 * len(rset & cset) / max(len(rset | cset), 1)
    return min(1.0, score)
