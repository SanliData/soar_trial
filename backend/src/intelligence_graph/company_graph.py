"""
INTELLIGENCE GRAPH: company_graph
PURPOSE: find_similar_companies, search_companies_by_industry; uses PostgreSQL + optional embeddings
"""
import logging
from typing import Any, Dict, List, Optional

from src.intelligence_graph.embedding_service import get_embedding, cosine_similarity

logger = logging.getLogger(__name__)


async def find_similar_companies(
    company_id: Optional[int] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
    db_session: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Find companies similar to the given company or industry/location.
    If company_id given and has embedding, use cosine similarity; else filter by industry/location.
    """
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
        except Exception:
            return []
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        if company_id:
            ref = db.query(IntelCompany).filter(IntelCompany.id == company_id).first()
            if ref and ref.embedding:
                all_companies = db.query(IntelCompany).filter(IntelCompany.id != company_id).limit(limit * 3).all()
                scored = []
                for c in all_companies:
                    if c.embedding:
                        sim = cosine_similarity(ref.embedding, c.embedding)
                        scored.append((sim, c))
                scored.sort(key=lambda x: -x[0])
                return [_company_to_dict(c) for _, c in scored[:limit]]
            ref = ref or db.query(IntelCompany).filter(IntelCompany.id == company_id).first()
            if ref:
                industry, location = ref.industry, ref.location
        q = db.query(IntelCompany)
        if industry:
            q = q.filter(IntelCompany.industry.ilike(f"%{industry}%"))
        if location:
            q = q.filter(IntelCompany.location.ilike(f"%{location}%"))
        companies = q.order_by(IntelCompany.created_at.desc()).limit(limit).all()
        return [_company_to_dict(c) for c in companies]
    except Exception as e:
        logger.warning("find_similar_companies failed: %s", e)
        return []
    finally:
        if db_session is None and "db" in dir():
            db.close()


async def search_companies_by_industry(
    industry: str,
    location: Optional[str] = None,
    limit: int = 50,
    db_session: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Search companies by industry (and optionally location)."""
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
        except Exception:
            return []
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        q = db.query(IntelCompany).filter(IntelCompany.industry.ilike(f"%{industry}%"))
        if location:
            q = q.filter(IntelCompany.location.ilike(f"%{location}%"))
        companies = q.order_by(IntelCompany.created_at.desc()).limit(limit).all()
        return [_company_to_dict(c) for c in companies]
    except Exception as e:
        logger.warning("search_companies_by_industry failed: %s", e)
        return []
    finally:
        if db_session is None and "db" in dir():
            db.close()


def _company_to_dict(c: Any) -> Dict[str, Any]:
    return {
        "id": c.id,
        "company_name": c.company_name,
        "website": c.website,
        "industry": c.industry,
        "location": c.location,
        "technologies": c.technologies,
        "description": c.description,
    }
