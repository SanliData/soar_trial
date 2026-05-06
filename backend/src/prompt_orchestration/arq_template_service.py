"""
MODULE: arq_template_service
PURPOSE: Structured ARQ checklists — explicit steps only (H-027)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_ARQ_TEMPLATE_IDS: frozenset[str] = frozenset(
    {
        "procurement_analysis",
        "opportunity_evaluation",
        "graph_confidence",
        "market_signal_validation",
    }
)

ARQ_TEMPLATES: dict[str, dict[str, Any]] = {
    "procurement_analysis": {
        "title": "Procurement analysis checklist",
        "steps": [
            "Identify buyer organisation and jurisdiction.",
            "List known solicitation identifiers or dates.",
            "Capture incumbent vs challenger hypothesis from evidence only.",
            "Flag missing mandatory fields explicitly.",
        ],
    },
    "opportunity_evaluation": {
        "title": "Opportunity evaluation checklist",
        "steps": [
            "Confirm geography and industry filters.",
            "Score fit against stated ICP constraints.",
            "List disqualifiers before ranking.",
            "Emit ranked list JSON matching opportunity_rank_v1 contract.",
        ],
    },
    "graph_confidence": {
        "title": "Graph confidence checklist",
        "steps": [
            "Enumerate entities and relationship types under review.",
            "Cross-check evidence source ids provided by ingestion.",
            "Surface conflicting edges if confidence differs materially.",
            "Do not infer undisclosed relationships.",
        ],
    },
    "market_signal_validation": {
        "title": "Market signal validation checklist",
        "steps": [
            "Verify signal timestamp / freshness window.",
            "Map signal to industry and region tags.",
            "Separate observation vs interpretation.",
            "State confidence tier (low/medium/high) with rationale pointers.",
        ],
    },
}


def export_arq_manifest() -> dict[str, Any]:
    rows = []
    for tid in sorted(ALLOWED_ARQ_TEMPLATE_IDS):
        meta = dict(ARQ_TEMPLATES[tid])
        meta["template_id"] = tid
        rows.append(meta)
    return {"arq_templates": rows}


def get_arq_template(template_id: str) -> dict[str, Any]:
    if template_id not in ALLOWED_ARQ_TEMPLATE_IDS:
        raise ValueError(f"unknown arq template: {template_id}")
    return dict(ARQ_TEMPLATES[template_id])
