"""
MODULE: chart_generation_service
PURPOSE: Metadata-driven chart generation (no raw JS) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.generative_operational_ui.safe_component_projection import project_safe_component

ALLOWED_CHARTS = {"bar_chart", "line_chart", "heatmap", "timeline_chart", "relationship_graph"}


def export_charts() -> dict[str, Any]:
    charts = []
    for t in sorted(ALLOWED_CHARTS):
        charts.append(
            project_safe_component(
                component_type="procurement_chart" if t != "heatmap" else "risk_heatmap",
                component_id=f"chart:{t}",
                props={"chart_type": t, "data_series": "metadata_only", "no_raw_js": True},
            )
        )
    return {"charts": charts, "deterministic": True, "metadata_only": True}

