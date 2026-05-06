"""
INTELLIGENCE_GRAPH: graph_store
PURPOSE: Persist and load semantic intelligence graph (nodes: company, contact, industry, campaign, message, geography; edges: company_has_contact, etc.)
"""
import json
import logging
from typing import Any, Dict, List, Optional

from src.intelligence_graph.models.node import Node, NodeType
from src.intelligence_graph.models.edge import Edge, EdgeType

logger = logging.getLogger(__name__)

STORE_KEY = "intelligence_graph:semantic"
STORE_TTL = 3600 * 24   # 24h


def _get_redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def load_semantic_graph(use_cache: bool = True) -> Dict[str, Any]:
    """Load semantic graph from Redis or return empty structure."""
    out = {"nodes": [], "edges": [], "nodes_by_id": {}, "edges_by_type": {}}
    if use_cache:
        redis = _get_redis()
        if redis:
            try:
                raw = redis.get(STORE_KEY)
                if raw:
                    data = json.loads(raw) if isinstance(raw, str) else raw
                    out["nodes"] = data.get("nodes", [])
                    out["edges"] = data.get("edges", [])
                    out["nodes_by_id"] = {n["id"]: n for n in out["nodes"]}
                    for e in out["edges"]:
                        t = e.get("type", "")
                        out["edges_by_type"].setdefault(t, []).append(e)
                    return out
            except Exception as e:
                logger.debug("graph_store load: %s", e)
    return out


def save_semantic_graph(graph: Dict[str, Any]) -> None:
    """Persist semantic graph to Redis."""
    redis = _get_redis()
    if not redis:
        return
    try:
        payload = {"nodes": graph.get("nodes", []), "edges": graph.get("edges", [])}
        redis.setex(STORE_KEY, STORE_TTL, json.dumps(payload))
    except Exception as e:
        logger.debug("graph_store save: %s", e)


def build_semantic_graph_from_db(db_session: Any = None) -> Dict[str, Any]:
    """
    Build semantic graph from relational DB: companies, contacts, industries, campaigns, messages.
    Nodes: company, contact, industry, campaign, message, geography.
    Edges: company_has_contact, company_belongs_to_industry, etc.
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    node_ids = set()
    close_session = False
    if db_session is None:
        try:
            from src.db.base import SessionLocal
            db = SessionLocal()
            close_session = True
        except Exception as e:
            logger.warning("graph_store: no db session: %s", e)
            return {"nodes": nodes, "edges": edges}
    else:
        db = db_session
    try:
        from src.models.intel_company import IntelCompany
        from src.models.intel_contact import IntelContact
        from src.models.intel_campaign import IntelCampaign
        industries_seen = set()
        geos_seen = set()
        for c in db.query(IntelCompany).limit(5000).all():
            nid = f"company_{c.id}"
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({
                    "id": nid,
                    "type": NodeType.company.value,
                    "label": c.company_name,
                    "properties": {"industry": c.industry, "location": c.location, "website": c.website},
                })
            if c.industry and c.industry not in industries_seen:
                industries_seen.add(c.industry)
                iid = f"industry_{c.industry.replace(' ', '_')}"
                nodes.append({"id": iid, "type": NodeType.industry.value, "label": c.industry, "properties": {}})
                edges.append({
                    "type": EdgeType.company_belongs_to_industry.value,
                    "source_id": nid,
                    "target_id": iid,
                    "properties": {},
                })
            if c.location and c.location not in geos_seen:
                geos_seen.add(c.location)
                gid = f"geo_{c.location.replace(' ', '_')[:50]}"
                nodes.append({"id": gid, "type": NodeType.geography.value, "label": c.location, "properties": {}})
        for r in db.query(IntelContact).limit(5000).all():
            nid = f"contact_{r.id}"
            if nid not in node_ids:
                node_ids.add(nid)
                nodes.append({
                    "id": nid,
                    "type": NodeType.contact.value,
                    "label": r.name,
                    "properties": {"role": r.role, "email": r.email},
                })
            cid = f"company_{r.company_id}"
            if cid in node_ids:
                edges.append({
                    "type": EdgeType.company_has_contact.value,
                    "source_id": cid,
                    "target_id": nid,
                    "properties": {},
                })
        for camp in db.query(IntelCampaign).limit(2000).all():
            cid = f"campaign_{camp.id}"
            if cid not in node_ids:
                node_ids.add(cid)
                nodes.append({
                    "id": cid,
                    "type": NodeType.campaign.value,
                    "label": camp.campaign_id or str(camp.id),
                    "properties": {"goal": camp.goal},
                })
        graph = {"nodes": nodes, "edges": edges}
        save_semantic_graph(graph)
        logger.info("graph_store: built %s nodes, %s edges", len(nodes), len(edges))
        return graph
    except Exception as e:
        logger.exception("graph_store build: %s", e)
        return {"nodes": nodes, "edges": edges}
    finally:
        if close_session and db:
            db.close()


def record_campaign_engagement_event(
    event_type: str,
    contact_id: int,
    campaign_id: int,
    company_id: int,
    message_id: Optional[int] = None,
) -> None:
    """
    Record a campaign event by adding an engagement node and edges to the semantic graph.
    event_type: contact_opened_message | contact_replied | company_engaged_with_campaign
    Campaign events should call this to update the graph.
    """
    import uuid
    redis = _get_redis()
    if not redis:
        return
    graph = load_semantic_graph(use_cache=True)
    nodes = list(graph.get("nodes", []))
    edges = list(graph.get("edges", []))
    node_ids = {n["id"] for n in nodes}
    cid = f"company_{company_id}"
    contact_nid = f"contact_{contact_id}"
    camp_nid = f"campaign_{campaign_id}"
    engagement_id = f"engagement_{uuid.uuid4().hex[:12]}"
    nodes.append({
        "id": engagement_id,
        "type": NodeType.engagement.value,
        "label": event_type,
        "properties": {"event_type": event_type, "contact_id": contact_id, "campaign_id": campaign_id, "company_id": company_id},
    })
    if event_type == "contact_opened_message":
        edges.append({
            "type": EdgeType.contact_opened_message.value,
            "source_id": contact_nid,
            "target_id": camp_nid if message_id is None else f"message_{message_id}",
            "properties": {},
        })
    elif event_type == "contact_replied":
        edges.append({
            "type": EdgeType.contact_replied.value,
            "source_id": contact_nid,
            "target_id": camp_nid,
            "properties": {},
        })
    edges.append({
        "type": EdgeType.company_engaged_with_campaign.value,
        "source_id": cid,
        "target_id": camp_nid,
        "properties": {"event_type": event_type},
    })
    save_semantic_graph({"nodes": nodes, "edges": edges})
    logger.debug("record_campaign_engagement_event: %s contact=%s campaign=%s", event_type, contact_id, campaign_id)
