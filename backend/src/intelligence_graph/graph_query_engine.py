"""
INTELLIGENCE_GRAPH: graph_query_engine
PURPOSE: Query the schema graph — join paths between tables, neighbors, valid table set
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from src.intelligence_graph.graph_builder import build_graph

logger = logging.getLogger(__name__)

_graph_cache: Optional[Dict[str, Any]] = None


def get_graph() -> Dict[str, Any]:
    """Return cached or freshly built graph."""
    global _graph_cache
    if _graph_cache is None:
        _graph_cache = build_graph(use_cache=True)
    return _graph_cache


def get_join_path(from_table: str, to_table: str, max_depth: int = 5) -> Optional[List[Tuple[str, str, str, str]]]:
    """
    Return a join path from from_table to to_table as list of (from_t, to_t, from_col, to_col).
    Uses BFS on the graph. Returns None if no path.
    """
    g = get_graph()
    edges = g.get("edges", [])
    adjacency = g.get("adjacency", {})
    if from_table not in adjacency or to_table not in adjacency:
        return None
    if from_table == to_table:
        return []
    parent: Dict[str, Tuple[str, str, str, str]] = {}
    from collections import deque
    q = deque([from_table])
    seen = {from_table}
    while q and len(seen) < 200:
        cur = q.popleft()
        if cur == to_table:
            path = []
            t = to_table
            max_steps = len(adjacency) + 1
            while t != from_table and t in parent and len(path) < max_steps:
                ft, tt, fc, tc = parent[t]
                path.append((ft, tt, fc, tc))
                t = ft if t == tt else tt  ***REMOVED*** previous node in path
            if t != from_table:
                return None
            path.reverse()
            return path
        for e in edges:
            if e["from_table"] == cur and e["to_table"] not in seen:
                n = e["to_table"]
                seen.add(n)
                parent[n] = (e["from_table"], e["to_table"], e["from_column"], e["to_column"])
                q.append(n)
            if e["to_table"] == cur and e["from_table"] not in seen:
                n = e["from_table"]
                seen.add(n)
                parent[n] = (e["from_table"], e["to_table"], e["from_column"], e["to_column"])
                q.append(n)
    return None


def get_table_columns(table_name: str) -> List[str]:
    """Return column names for a table from the graph."""
    g = get_graph()
    return g.get("table_columns", {}).get(table_name, [])


def list_tables() -> List[str]:
    """Return all table names in the schema graph."""
    g = get_graph()
    return list(g.get("table_columns", {}).keys())


***REMOVED*** ---- Semantic graph queries (company, contact, industry, campaign, message, geography) ----


def similar_companies(
    company_id: Optional[int] = None,
    industry: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """Return companies similar to the given company or industry/location (uses intel_companies + optional embeddings)."""
    try:
        from src.intelligence_graph.company_graph import find_similar_companies
        import asyncio
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                find_similar_companies(company_id=company_id, industry=industry, location=location, limit=limit)
            )
            return result or []
        finally:
            loop.close()
    except Exception as e:
        logger.debug("similar_companies: %s", e)
        return []


def high_response_industries(limit: int = 20) -> List[Dict[str, Any]]:
    """Return industries with highest reply rates (from industry_performance)."""
    try:
        from src.db.base import SessionLocal
        from src.models.industry_performance import IndustryPerformance
        db = SessionLocal()
        try:
            rows = (
                db.query(IndustryPerformance.industry, IndustryPerformance.reply_rate, IndustryPerformance.replies_received)
                .filter(IndustryPerformance.reply_rate.isnot(None))
                .order_by(IndustryPerformance.reply_rate.desc())
                .limit(limit)
                .all()
            )
            return [{"industry": r[0], "reply_rate": r[1], "replies_received": r[2]} for r in rows]
        finally:
            db.close()
        return []
    except Exception as e:
        logger.debug("high_response_industries: %s", e)
        return []


def role_response_correlations(limit: int = 50) -> List[Dict[str, Any]]:
    """Return role (title) vs response correlation from contacts/campaign outcomes (aggregate by role)."""
    try:
        from src.db.base import SessionLocal
        from src.models.intel_contact import IntelContact
        from sqlalchemy import func
        db = SessionLocal()
        try:
            rows = (
                db.query(IntelContact.role, func.count(IntelContact.id).label("count"))
                .filter(IntelContact.role.isnot(None))
                .group_by(IntelContact.role)
                .order_by(func.count(IntelContact.id).desc())
                .limit(limit)
                .all()
            )
            return [{"role": r[0], "contact_count": r[1]} for r in rows]
        finally:
            db.close()
        return []
    except Exception as e:
        logger.debug("role_response_correlations: %s", e)
        return []


def engagement_clusters(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return clusters of engagement (e.g. by campaign): groups of companies/contacts with shared engagement.
    Uses semantic graph edges: contact_opened_message, contact_replied, company_engaged_with_campaign.
    """
    try:
        from src.intelligence_graph.graph_store import load_semantic_graph
        g = load_semantic_graph(use_cache=True)
        edges = g.get("edges", [])
        nodes_by_id = g.get("nodes_by_id") or {n["id"]: n for n in g.get("nodes", [])}
        engagement_types = ("contact_opened_message", "contact_replied", "company_engaged_with_campaign")
        campaign_engagement: Dict[str, List[str]] = {}
        for e in edges:
            t = e.get("type", "")
            if t not in engagement_types:
                continue
            camp = e.get("target_id", "")
            if not camp.startswith("campaign_"):
                continue
            campaign_engagement.setdefault(camp, []).append(e.get("source_id", ""))
        clusters = []
        for camp_id, source_ids in list(campaign_engagement.items())[:limit]:
            label = (nodes_by_id.get(camp_id) or {}).get("label", camp_id)
            clusters.append({
                "campaign_id": camp_id,
                "label": label,
                "engaged_count": len(source_ids),
                "source_ids": source_ids[:50],
            })
        clusters.sort(key=lambda x: -x["engaged_count"])
        return clusters[:limit]
    except Exception as e:
        logger.debug("engagement_clusters: %s", e)
        return []


def high_engagement_companies(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return companies with the most engagement (company_engaged_with_campaign edges).
    """
    try:
        from src.intelligence_graph.graph_store import load_semantic_graph
        g = load_semantic_graph(use_cache=True)
        edges = g.get("edges", [])
        nodes_by_id = g.get("nodes_by_id") or {n["id"]: n for n in g.get("nodes", [])}
        company_count: Dict[str, int] = {}
        for e in edges:
            if e.get("type") != "company_engaged_with_campaign":
                continue
            cid = e.get("source_id", "")
            if cid.startswith("company_"):
                company_count[cid] = company_count.get(cid, 0) + 1
        out = []
        for cid, count in sorted(company_count.items(), key=lambda x: -x[1])[:limit]:
            node = nodes_by_id.get(cid, {})
            out.append({
                "company_id": cid,
                "label": node.get("label", cid),
                "engagement_count": count,
                "properties": node.get("properties", {}),
            })
        return out
    except Exception as e:
        logger.debug("high_engagement_companies: %s", e)
        return []
