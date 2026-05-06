"""
MODULE: json_contract_service
PURPOSE: Approved structured output contracts (schema summaries, not arbitrary JSON) (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

# Summaries use JSON-Schema-like keys for deterministic validation in evaluation — no free-form trees.
JSON_CONTRACTS: dict[str, dict[str, Any]] = {
    "results_hub_v1": {
        "description": "Results Hub artefact bundle",
        "type": "object",
        "required": ["plan_id", "companies", "meta"],
        "properties": {
            "plan_id": {"type": "string"},
            "companies": {"type": "array"},
            "meta": {"type": "object"},
        },
    },
    "widget_render_v1": {
        "description": "Intelligence widget render envelope",
        "type": "object",
        "required": ["widget_type", "visualization_type", "data"],
        "properties": {
            "widget_type": {"type": "string"},
            "visualization_type": {"type": "string"},
            "data": {"type": "object"},
        },
    },
    "graph_insight_v1": {
        "description": "Commercial graph traversal insight",
        "type": "object",
        "required": ["seed_entity_id", "visited_entity_ids", "traversal_edges"],
        "properties": {
            "seed_entity_id": {"type": "string"},
            "visited_entity_ids": {"type": "array"},
            "traversal_edges": {"type": "array"},
        },
    },
    "opportunity_rank_v1": {
        "description": "Ranked opportunity list",
        "type": "object",
        "required": ["opportunities", "ranking_notes"],
        "properties": {
            "opportunities": {"type": "array"},
            "ranking_notes": {"type": "array"},
        },
    },
}


def list_contract_ids() -> list[str]:
    return sorted(JSON_CONTRACTS.keys())


def get_contract(contract_id: str) -> dict[str, Any]:
    if contract_id not in JSON_CONTRACTS:
        raise ValueError(f"unknown contract_id: {contract_id}")
    return dict(JSON_CONTRACTS[contract_id])


def export_contracts_manifest() -> dict[str, Any]:
    return {"contracts": [{"contract_id": k, **JSON_CONTRACTS[k]} for k in sorted(JSON_CONTRACTS.keys())]}
