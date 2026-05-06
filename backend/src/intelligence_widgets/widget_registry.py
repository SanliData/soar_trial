"""
MODULE: widget_registry
PURPOSE: Approved widget type definitions — static registry only (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Mapping

from src.intelligence_widgets.widget_contracts import ALLOWED_VISUALIZATION_TYPES

***REMOVED*** widget_type -> allowed visualization_type values (deterministic allow-list).
WIDGET_VISUALIZATION_ALLOWLIST: dict[str, frozenset[str]] = {
    "opportunity_cluster_map": frozenset({"map", "card"}),
    "market_signal_chart": frozenset({"chart", "card"}),
    "executive_summary_card": frozenset({"card"}),
    "exposure_funnel": frozenset({"chart", "card"}),
    "graph_relationship_view": frozenset({"graph", "table"}),
    "procurement_timeline": frozenset({"timeline", "table"}),
    "onboarding_progress": frozenset({"card", "timeline"}),
}

WIDGET_METADATA: dict[str, Mapping[str, Any]] = {
    "opportunity_cluster_map": {
        "label": "Opportunity cluster map",
        "domain": "opportunity_engine",
        "summary": "Bounded geographic / sector cluster summary for planning surfaces.",
    },
    "market_signal_chart": {
        "label": "Market signal chart",
        "domain": "market_signals",
        "summary": "Structured signal strengths over time or categories.",
    },
    "executive_summary_card": {
        "label": "Executive summary card",
        "domain": "results_hub",
        "summary": "Concise intelligence headline with provenance hints.",
    },
    "exposure_funnel": {
        "label": "Exposure funnel",
        "domain": "precision_exposure",
        "summary": "Stage counts for exposure progression analytics.",
    },
    "graph_relationship_view": {
        "label": "Graph relationship view",
        "domain": "company_graph",
        "summary": "Vertices and edges as lists — no remote graph runtime.",
    },
    "procurement_timeline": {
        "label": "Procurement timeline",
        "domain": "procurement",
        "summary": "Ordered milestones with dates as structured rows.",
    },
    "onboarding_progress": {
        "label": "Onboarding progress",
        "domain": "onboarding",
        "summary": "Step completion snapshot for guided workflows.",
    },
}


def list_registered_widget_types() -> list[str]:
    return sorted(WIDGET_METADATA.keys())


def export_registry_public() -> dict[str, Any]:
    """Deterministic manifest for GET /types."""
    types_out: list[dict[str, Any]] = []
    for wt in sorted(WIDGET_METADATA.keys()):
        meta = dict(WIDGET_METADATA[wt])
        meta["widget_type"] = wt
        meta["allowed_visualizations"] = sorted(WIDGET_VISUALIZATION_ALLOWLIST.get(wt, frozenset()))
        types_out.append(meta)
    return {
        "widget_types": types_out,
        "visualization_types_allowed_globally": sorted(ALLOWED_VISUALIZATION_TYPES),
    }


def allowed_visualizations_for(widget_type: str) -> frozenset[str]:
    return WIDGET_VISUALIZATION_ALLOWLIST.get(widget_type, frozenset())
