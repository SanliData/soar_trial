"""
COMPANY_GRAPH: graph_query_engine
PURPOSE: Query graph — get company by id, neighbors, edges by type
"""
import logging
from typing import Any, Dict, List, Optional

from src.company_graph.graph_store import load_graph

logger = logging.getLogger(__name__)


def get_company_node(company_id: int) -> Optional[Dict[str, Any]]:
    """Return node for company id or None."""
    g = load_graph()
    nid = f"company_{company_id}"
    for n in g.get("nodes", []):
        if n.get("id") == nid:
            return n
    return None


def get_company_contacts(company_id: int) -> List[Dict[str, Any]]:
    """Return contact nodes linked to company."""
    g = load_graph()
    nid = f"company_{company_id}"
    contact_ids = set()
    for e in g.get("edges", []):
        if e.get("type") == "company_has_contact" and e.get("source_id") == nid:
            contact_ids.add(e.get("target_id"))
    out = []
    for n in g.get("nodes", []):
        if n.get("id") in contact_ids:
            out.append(n)
    return out


def get_edges_from(node_id: str, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return edges from node_id, optionally filtered by type."""
    g = load_graph()
    out = []
    for e in g.get("edges", []):
        if e.get("source_id") != node_id:
            continue
        if edge_type and e.get("type") != edge_type:
            continue
        out.append(e)
    return out
