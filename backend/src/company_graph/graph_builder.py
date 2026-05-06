import logging
from typing import Any, Dict

from src.company_graph.relationship_extractor import extract_company_relationships

logger = logging.getLogger(__name__)


def build_graph(db_session: Any = None) -> Dict[str, Any]:
    close = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close = True
        except Exception as e:
            logger.warning("graph_builder: no db: %s", e)
            return {"nodes": [], "edges": []}
    else:
        db = db_session
    try:
        data = extract_company_relationships(db)
        logger.info("graph_builder: %s nodes, %s edges", len(data["nodes"]), len(data["edges"]))
        return data
    finally:
        if close and db:
            db.close()
