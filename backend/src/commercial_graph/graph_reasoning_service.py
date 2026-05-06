"""
MODULE: graph_reasoning_service
PURPOSE: Explainable deterministic graph insights (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.commercial_graph import commercial_graph_builder as gb
from src.commercial_graph.entity_schema import CommercialRelationship
from src.commercial_graph.graph_confidence_service import explain_confidence_factors
from src.commercial_graph.relationship_registry import RELATIONSHIP_METADATA


def explain_relationship(relationship_id: str) -> dict[str, Any]:
    rel = gb.all_relationship_map().get(relationship_id)
    if not rel:
        raise ValueError("relationship not found")
    src = gb.get_entity(rel.source_entity_id)
    tgt = gb.get_entity(rel.target_entity_id)
    if not src or not tgt:
        raise ValueError("relationship endpoints missing")
    meta = dict(RELATIONSHIP_METADATA.get(rel.relationship_type, {}))
    repetition = sum(
        1
        for r in gb.all_relationship_map().values()
        if r.relationship_id != rel.relationship_id and _same_edge(r, rel)
    )
    factors = explain_confidence_factors(
        source=src,
        target=tgt,
        evidence_sources=list(rel.evidence_sources),
        repetition_count=repetition,
    )
    return {
        "relationship_id": relationship_id,
        "relationship_type": rel.relationship_type,
        "registry_semantics": meta.get("commercial_semantics", ""),
        "confidence_score": rel.confidence_score,
        "confidence_factors": factors,
        "evidence_sources": list(rel.evidence_sources),
        "source": {"entity_id": src.entity_id, "name": src.name, "entity_type": src.entity_type},
        "target": {"entity_id": tgt.entity_id, "name": tgt.name, "entity_type": tgt.entity_type},
    }


def _same_edge(a: CommercialRelationship, b: CommercialRelationship) -> bool:
    return (
        a.relationship_type == b.relationship_type
        and {a.source_entity_id, a.target_entity_id} == {b.source_entity_id, b.target_entity_id}
    )


def summarize_entity_context(entity_id: str) -> dict[str, Any]:
    ent = gb.get_entity(entity_id)
    if not ent:
        raise ValueError("entity not found")
    summary = gb.list_relationships(source_entity_id=entity_id)
    neighbor_names: list[dict[str, str]] = []
    for r in summary:
        other = r.target_entity_id if r.source_entity_id == entity_id else r.source_entity_id
        o = gb.get_entity(other)
        if o:
            neighbor_names.append({"entity_id": o.entity_id, "name": o.name, "relationship_type": r.relationship_type})
    return {
        "entity": ent.model_dump(mode="json"),
        "neighbor_summary": sorted(neighbor_names, key=lambda x: x["entity_id"]),
        "relationship_count": len(summary),
    }


def identify_high_confidence_clusters(*, min_confidence: float = 0.72) -> dict[str, Any]:
    """Connected components on edges meeting confidence threshold — deterministic ordering."""
    edges = [r for r in gb.all_relationship_map().values() if r.confidence_score >= min_confidence]
    parent: dict[str, str] = {}

    def find(x: str) -> str:
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra < rb:
                parent[rb] = ra
            else:
                parent[ra] = rb

    for r in edges:
        union(r.source_entity_id, r.target_entity_id)

    groups: dict[str, list[str]] = {}
    for r in edges:
        for n in (r.source_entity_id, r.target_entity_id):
            root = find(n)
            groups.setdefault(root, []).append(n)
    clusters = []
    for root in sorted(groups.keys()):
        members = sorted(set(groups[root]))
        clusters.append({"representative": root, "entity_ids": members, "size": len(members)})
    clusters.sort(key=lambda c: (-c["size"], c["representative"]))
    return {"min_confidence": min_confidence, "clusters": clusters, "edge_count": len(edges)}
