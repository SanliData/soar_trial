"""
MODULE: relationship_registry
PURPOSE: Static approved relationship definitions (H-026)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Mapping

from src.commercial_graph.entity_schema import ALLOWED_RELATIONSHIP_TYPES

RELATIONSHIP_METADATA: dict[str, Mapping[str, Any]] = {
    "contracts_with": {
        "label": "Contracts with",
        "directionality": "directed",
        "commercial_semantics": "Procurement or service contract linkage.",
    },
    "funds_project": {
        "label": "Funds project",
        "directionality": "directed",
        "commercial_semantics": "Capital flow into infrastructure or procurement.",
    },
    "operates_in": {
        "label": "Operates in",
        "directionality": "directed",
        "commercial_semantics": "Geographic or regulatory presence.",
    },
    "competes_with": {
        "label": "Competes with",
        "directionality": "undirected",
        "commercial_semantics": "Market overlap signal.",
    },
    "partners_with": {
        "label": "Partners with",
        "directionality": "undirected",
        "commercial_semantics": "Alliance or JV-style linkage.",
    },
    "related_to": {
        "label": "Related to",
        "directionality": "undirected",
        "commercial_semantics": "General associative tie with explicit evidence.",
    },
    "supplies": {
        "label": "Supplies",
        "directionality": "directed",
        "commercial_semantics": "Supply-chain dependency.",
    },
    "influences": {
        "label": "Influences",
        "directionality": "directed",
        "commercial_semantics": "Policy or market influence.",
    },
}


def validate_relationship_type(relationship_type: str) -> None:
    if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
        raise ValueError(f"unknown relationship_type: {relationship_type}")
    if relationship_type not in RELATIONSHIP_METADATA:
        raise ValueError(f"missing registry metadata for {relationship_type}")


def export_registry() -> dict[str, Any]:
    rows = []
    for rt in sorted(ALLOWED_RELATIONSHIP_TYPES):
        meta = dict(RELATIONSHIP_METADATA[rt])
        meta["relationship_type"] = rt
        rows.append(meta)
    return {"relationship_types": rows}
