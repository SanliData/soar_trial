"""
MODULE: ui_component_registry
PURPOSE: Approved operational UI component registry (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ALLOWED_COMPONENT_TYPES = {
    "operational_dashboard",
    "procurement_chart",
    "risk_heatmap",
    "contractor_graph",
    "timeline_view",
    "approval_panel",
    "retrieval_lineage_view",
    "workflow_trace_view",
}


def export_ui_component_registry() -> dict[str, Any]:
    rows = []
    for t in sorted(ALLOWED_COMPONENT_TYPES):
        rows.append(
            {
                "component_type": t,
                "approved": True,
                "metadata_only": True,
                "no_unrestricted_html_generation": True,
                "deterministic": True,
            }
        )
    return {"component_types": rows, "deterministic": True}
