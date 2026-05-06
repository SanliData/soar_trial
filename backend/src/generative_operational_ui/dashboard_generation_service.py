"""
MODULE: dashboard_generation_service
PURPOSE: Governed dashboard generation from approved components (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.generative_operational_ui.chart_generation_service import export_charts
from src.generative_operational_ui.graph_visualization_service import export_graph_views
from src.generative_operational_ui.safe_component_projection import project_safe_component


def export_dashboards() -> dict[str, Any]:
    charts = export_charts()["charts"]
    graphs = export_graph_views()["graphs"]
    dashboards = [
        {
            "dashboard_id": "dash:procurement_overview",
            "components": [
                project_safe_component(
                    component_type="operational_dashboard",
                    component_id="op:summary",
                    props={"summary": "procurement overview (metadata-only)", "explainability_mandatory": True},
                ),
                *charts[:2],
                *graphs[:1],
            ],
            "deterministic": True,
            "explainability_mandatory": True,
            "no_unrestricted_generated_actions": True,
        },
        {
            "dashboard_id": "dash:governance_and_approvals",
            "components": [
                project_safe_component(
                    component_type="approval_panel",
                    component_id="approval:panel",
                    props={"source": "hitl_runtime", "metadata_only": True},
                ),
                project_safe_component(
                    component_type="timeline_view",
                    component_id="timeline:event_stream",
                    props={"source": "agui_runtime", "metadata_only": True},
                ),
            ],
            "deterministic": True,
            "explainability_mandatory": True,
            "no_unrestricted_generated_actions": True,
        },
    ]
    return {"dashboards": dashboards, "deterministic": True, "governed_components_only": True}

