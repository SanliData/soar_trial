"""
INTELLIGENCE_GRAPH: graph_builder
PURPOSE: Read DB metadata, detect FKs, build graph structure; store in memory or Redis cache
"""
import json
import logging
from typing import Any, Dict, List, Optional

from src.intelligence_graph.models.graph_node import GraphNode
from src.intelligence_graph.models.graph_edge import GraphEdge
from src.intelligence_graph.schema_mapper import get_tables_from_metadata
from src.intelligence_graph.relationship_extractor import extract_foreign_keys

logger = logging.getLogger(__name__)

GRAPH_CACHE_KEY = "intelligence_graph:schema"
GRAPH_CACHE_TTL = 3600 * 24   # 24h


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def build_graph(use_cache: bool = True) -> Dict[str, Any]:
    """
    Build schema graph: nodes from tables, edges from FKs.
    Returns { "nodes": [...], "edges": [...], "adjacency": { table: [neighbor tables] } }.
    If use_cache and Redis available, read from cache when present.
    """
    redis = _get_redis()
    if use_cache and redis:
        try:
            raw = redis.get(GRAPH_CACHE_KEY)
            if raw:
                return json.loads(raw) if isinstance(raw, str) else raw
        except Exception as e:
            logger.debug("graph_builder cache get: %s", e)
    nodes = get_tables_from_metadata()
    edges = extract_foreign_keys()
    node_map = {n.table_name: n.model_dump() for n in nodes}
    edge_list = [e.model_dump() for e in edges]
    adjacency: Dict[str, List[str]] = {}
    for n in nodes:
        adjacency[n.table_name] = []
    for e in edges:
        if e.from_table in adjacency:
            adjacency[e.from_table].append(e.to_table)
        rev = e.to_table
        if rev not in adjacency:
            adjacency[rev] = []
        if e.from_table not in adjacency[rev]:
            adjacency[rev].append(e.from_table)
    graph = {
        "nodes": list(node_map.values()),
        "edges": edge_list,
        "adjacency": adjacency,
        "table_columns": {n.table_name: n.columns for n in nodes},
    }
    if redis:
        try:
            redis.setex(GRAPH_CACHE_KEY, GRAPH_CACHE_TTL, json.dumps(graph))
        except Exception as e:
            logger.debug("graph_builder cache set: %s", e)
    logger.info("graph_builder: built graph with %s nodes, %s edges", len(nodes), len(edges))
    return graph


def refresh_graph_cache() -> Dict[str, Any]:
    """Force rebuild and cache (e.g. on startup or scheduled refresh)."""
    return build_graph(use_cache=False)
