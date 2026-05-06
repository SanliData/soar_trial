"""
MODULE: capability_validation_service
PURPOSE: Validate capability ids, edges, contracts, topology integrity (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.semantic_capability_graph.capability_graph_registry import SEMANTIC_CAPABILITY_ENTITIES
from src.semantic_capability_graph.capability_relationship_service import (
    RELATIONSHIP_TYPES,
    SEMANTIC_RELATIONSHIPS,
)
from src.semantic_capability_graph.semantic_contract_service import SEMANTIC_CONTRACTS


def validate_capability_id(capability_id: str) -> None:
    if capability_id not in SEMANTIC_CAPABILITY_ENTITIES:
        raise ValueError(f"unknown semantic capability: {capability_id}")


def validate_relationship_triple(source: str, rel: str, target: str) -> None:
    validate_capability_id(source)
    validate_capability_id(target)
    if rel not in RELATIONSHIP_TYPES:
        raise ValueError(f"invalid relationship type: {rel}")
    if (source, rel, target) not in SEMANTIC_RELATIONSHIPS:
        raise ValueError("relationship not in approved static graph")


def validate_topology_integrity() -> None:
    for s, r, t in SEMANTIC_RELATIONSHIPS:
        validate_relationship_triple(s, r, t)


def validate_contract_record(contract: dict[str, Any]) -> None:
    src = contract.get("source_capability")
    tgt = contract.get("target_capability")
    if not isinstance(src, str) or not isinstance(tgt, str):
        raise ValueError("contract requires source_capability and target_capability strings")
    validate_capability_id(src)
    validate_capability_id(tgt)


def validate_all_contracts() -> None:
    for c in SEMANTIC_CONTRACTS:
        validate_contract_record(c)


def validate_trust_relationship(source: str, target: str) -> None:
    """Ensure a directed trust-class edge exists (source → target)."""
    validate_capability_id(source)
    validate_capability_id(target)
    ok = any(
        s == source and t == target and r in ("trusted_by", "secured_by")
        for s, r, t in SEMANTIC_RELATIONSHIPS
    )
    if not ok:
        raise ValueError("no static trust relationship for given ordered pair")
