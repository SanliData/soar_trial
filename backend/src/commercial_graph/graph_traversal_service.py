"""
MODULE: graph_traversal_service
PURPOSE: Deterministic BFS-style graph traversal (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from src.commercial_graph import commercial_graph_builder as gb
def get_connected_entities(
    entity_id: str,
    *,
    depth: int = 2,
    relationship_type: Optional[str] = None,
) -> dict[str, Any]:
    if depth < 1:
        depth = 1
    if gb.get_entity(entity_id) is None:
        raise ValueError("unknown entity_id")
    visited: set[str] = {entity_id}
    frontier: deque[tuple[str, int]] = deque([(entity_id, 0)])
    edges_used: list[dict[str, str]] = []
    while frontier:
        cur, d = frontier.popleft()
        if d >= depth:
            continue
        for rel_id, nb, rtype in gb.iter_neighbors(cur):
            if relationship_type and rtype != relationship_type:
                continue
            edges_used.append(
                {"relationship_id": rel_id, "from": cur, "to": nb, "relationship_type": rtype}
            )
            if nb not in visited:
                visited.add(nb)
                frontier.append((nb, d + 1))
    entities_out = [gb.get_entity(eid) for eid in sorted(visited)]
    entities_out = [e for e in entities_out if e is not None]
    return {
        "seed_entity_id": entity_id,
        "depth": depth,
        "visited_entity_ids": sorted(visited),
        "entities": [e.model_dump(mode="json") for e in entities_out],
        "traversal_edges": sorted(edges_used, key=lambda x: x["relationship_id"]),
    }


def get_relationship_path(source_entity_id: str, target_entity_id: str) -> dict[str, Any]:
    if gb.get_entity(source_entity_id) is None or gb.get_entity(target_entity_id) is None:
        raise ValueError("unknown entity endpoint")
    if source_entity_id == target_entity_id:
        return {"path_found": True, "entity_ids": [source_entity_id], "relationship_ids": []}
    prev: dict[str, tuple[str, str]] = {}
    q: deque[str] = deque([source_entity_id])
    seen = {source_entity_id}
    found = False
    while q:
        cur = q.popleft()
        if cur == target_entity_id:
            found = True
            break
        for rel_id, nb, _rtype in gb.iter_neighbors(cur):
            if nb not in seen:
                seen.add(nb)
                prev[nb] = (cur, rel_id)
                q.append(nb)
    if not found:
        return {"path_found": False, "entity_ids": [], "relationship_ids": []}
    node = target_entity_id
    ent_rev = [node]
    rel_rev: list[str] = []
    while node != source_entity_id:
        pnode, rid = prev[node]
        rel_rev.append(rid)
        ent_rev.append(pnode)
        node = pnode
    ent_rev.reverse()
    rel_rev.reverse()
    return {"path_found": True, "entity_ids": ent_rev, "relationship_ids": rel_rev}


def find_related_opportunities(entity_id: str, *, depth: int = 3) -> dict[str, Any]:
    conn = get_connected_entities(entity_id, depth=depth)
    clusters = [
        e
        for e in conn["entities"]
        if isinstance(e, dict) and e.get("entity_type") == "opportunity_cluster"
    ]
    return {
        "seed_entity_id": entity_id,
        "depth": depth,
        "opportunity_clusters": clusters,
        "count": len(clusters),
    }


def summarize_relationships(entity_id: str) -> dict[str, Any]:
    rels = gb.list_relationships(source_entity_id=entity_id)
    by_type: dict[str, int] = {}
    for r in rels:
        by_type[r.relationship_type] = by_type.get(r.relationship_type, 0) + 1
    conf_vals = [r.confidence_score for r in rels]
    avg_conf = round(sum(conf_vals) / len(conf_vals), 4) if conf_vals else 0.0
    return {
        "entity_id": entity_id,
        "relationship_count": len(rels),
        "by_relationship_type": dict(sorted(by_type.items())),
        "average_confidence": avg_conf,
    }


def traverse_payload(
    entity_id: str,
    *,
    depth: int = 2,
    relationship_type: Optional[str] = None,
    include_opportunities: bool = False,
    path_to: Optional[str] = None,
) -> dict[str, Any]:
    conn = get_connected_entities(entity_id, depth=depth, relationship_type=relationship_type)
    out: dict[str, Any] = {"connected": conn}
    if include_opportunities:
        out["opportunities"] = find_related_opportunities(entity_id, depth=depth)
    if path_to:
        out["path"] = get_relationship_path(entity_id, path_to)
    out["summary"] = summarize_relationships(entity_id)
    return out
