"""
MODULE: commercial_graph_builder
PURPOSE: In-memory adjacency-list commercial graph (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from src.commercial_graph.entity_schema import (
    ALLOWED_ENTITY_TYPES,
    CommercialEntity,
    CommercialRelationship,
    CreateCommercialEntityRequest,
    CreateCommercialRelationshipRequest,
)
from src.commercial_graph.graph_confidence_service import compute_relationship_confidence
from src.commercial_graph.relationship_registry import validate_relationship_type

_ENTITIES: dict[str, CommercialEntity] = {}
_RELATIONSHIPS: dict[str, CommercialRelationship] = {}
***REMOVED*** entity_id -> list of (relationship_id, neighbor_id, relationship_type)
_ADJ_OUT: dict[str, list[tuple[str, str, str]]] = {}


def clear_graph_for_tests() -> None:
    _ENTITIES.clear()
    _RELATIONSHIPS.clear()
    _ADJ_OUT.clear()


def get_entity(entity_id: str) -> CommercialEntity | None:
    return _ENTITIES.get(entity_id)


def list_entities() -> list[CommercialEntity]:
    return list(_ENTITIES.values())


def list_relationships(
    *,
    source_entity_id: Optional[str] = None,
    min_confidence: Optional[float] = None,
) -> list[CommercialRelationship]:
    rows = list(_RELATIONSHIPS.values())
    if source_entity_id:
        rows = [r for r in rows if r.source_entity_id == source_entity_id or r.target_entity_id == source_entity_id]
    if min_confidence is not None:
        rows = [r for r in rows if r.confidence_score >= min_confidence]
    rows.sort(key=lambda r: r.relationship_id)
    return rows


def _add_adj(a: str, b: str, rel_id: str, rel_type: str) -> None:
    _ADJ_OUT.setdefault(a, []).append((rel_id, b, rel_type))
    _ADJ_OUT.setdefault(b, []).append((rel_id, a, rel_type))


def _count_same_triple(source_id: str, target_id: str, rel_type: str) -> int:
    n = 0
    for r in _RELATIONSHIPS.values():
        if r.relationship_type != rel_type:
            continue
        if {r.source_entity_id, r.target_entity_id} == {source_id, target_id}:
            n += 1
    return n


def create_entity(body: CreateCommercialEntityRequest) -> CommercialEntity:
    if body.entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(f"invalid entity_type: {body.entity_type}")
    eid = str(uuid.uuid4())
    ent = CommercialEntity(
        entity_id=eid,
        entity_type=body.entity_type,
        name=body.name,
        description=body.description,
        geographic_scope=body.geographic_scope,
        authority_score=body.authority_score,
        freshness_days=body.freshness_days,
        metadata=dict(body.metadata),
        created_at=datetime.now(timezone.utc),
        tags=list(body.tags),
    )
    _ENTITIES[eid] = ent
    return ent


def create_relationship(body: CreateCommercialRelationshipRequest) -> CommercialRelationship:
    validate_relationship_type(body.relationship_type)
    src = _ENTITIES.get(body.source_entity_id)
    tgt = _ENTITIES.get(body.target_entity_id)
    if not src or not tgt:
        raise ValueError("source or target entity not found")
    if src.entity_id == tgt.entity_id:
        raise ValueError("self-loop not permitted in foundation graph")
    repetition = _count_same_triple(body.source_entity_id, body.target_entity_id, body.relationship_type)
    conf = compute_relationship_confidence(
        source=src,
        target=tgt,
        relationship_type=body.relationship_type,
        evidence_sources=list(body.evidence_sources),
        repetition_count=repetition,
    )
    rid = str(uuid.uuid4())
    rel = CommercialRelationship(
        relationship_id=rid,
        source_entity_id=body.source_entity_id,
        target_entity_id=body.target_entity_id,
        relationship_type=body.relationship_type,
        confidence_score=conf,
        evidence_sources=list(body.evidence_sources),
        created_at=datetime.now(timezone.utc),
    )
    _RELATIONSHIPS[rid] = rel
    _add_adj(body.source_entity_id, body.target_entity_id, rid, body.relationship_type)
    return rel


def adjacency_snapshot() -> dict[str, list[tuple[str, str, str]]]:
    return {k: list(v) for k, v in _ADJ_OUT.items()}


def all_relationship_map() -> dict[str, CommercialRelationship]:
    return dict(_RELATIONSHIPS)


def iter_neighbors(entity_id: str) -> list[tuple[str, str, str]]:
    """Yield (relationship_id, neighbor_id, relationship_type) for undirected traversal."""
    return list(_ADJ_OUT.get(entity_id, []))
