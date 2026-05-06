import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)
GRAPH_KEY = "company_graph:data"
GRAPH_TTL = 3600 * 24


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def load_graph(use_cache: bool = True) -> Dict[str, Any]:
    if use_cache:
        r = _redis()
        if r:
            try:
                raw = r.get(GRAPH_KEY)
                if raw:
                    return json.loads(raw) if isinstance(raw, str) else raw
            except Exception as e:
                logger.debug("graph_store load: %s", e)
    return {"nodes": [], "edges": []}


def save_graph(graph: Dict[str, Any]) -> None:
    r = _redis()
    if r:
        try:
            r.setex(GRAPH_KEY, GRAPH_TTL, json.dumps(graph))
        except Exception as e:
            logger.debug("graph_store save: %s", e)


def refresh_graph(db_session: Any = None) -> Dict[str, Any]:
    from src.company_graph.graph_builder import build_graph
    graph = build_graph(db_session)
    save_graph(graph)
    return graph
