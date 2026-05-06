"""
MODULE: graph_visualization_service
PURPOSE: Deterministic graph visualization metadata with lineage requirement (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.generative_operational_ui.safe_component_projection import project_safe_component


def export_graph_views() -> dict[str, Any]:
    views = [
        project_safe_component(
            component_type="contractor_graph",
            component_id="graph:contractor_relationships",
            props={"graph_type": "contractor_relationships", "lineage_required": True},
        ),
        project_safe_component(
            component_type="workflow_trace_view",
            component_id="graph:workflow_lineage",
            props={"graph_type": "workflow_lineage", "lineage_required": True},
        ),
        project_safe_component(
            component_type="approval_panel",
            component_id="graph:approval_escalation_chains",
            props={"graph_type": "approval_escalation_chains", "lineage_required": True},
        ),
    ]
    return {"graphs": views, "deterministic": True, "graph_lineage_required": True}

