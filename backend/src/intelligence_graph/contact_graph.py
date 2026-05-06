"""
INTELLIGENCE GRAPH: contact_graph
PURPOSE: get_company_contacts — contacts for a company from PostgreSQL
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


async def get_company_contacts(
    company_id: int,
    roles: Optional[List[str]] = None,
    limit: int = 50,
    db_session: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Return contacts for a company (optionally filter by roles)."""
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
        except Exception:
            return []
    else:
        db = db_session
    try:
        from src.models.intel_contact import IntelContact
        q = db.query(IntelContact).filter(IntelContact.company_id == company_id)
        if roles:
            q = q.filter(IntelContact.role.in_(roles))
        contacts = q.order_by(IntelContact.created_at.desc()).limit(limit).all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "role": c.role,
                "linkedin_url": c.linkedin_url,
                "email": c.email,
                "company_id": c.company_id,
            }
            for c in contacts
        ]
    except Exception as e:
        logger.warning("get_company_contacts failed: %s", e)
        return []
    finally:
        if db_session is None and "db" in dir():
            db.close()
