"""
MODULE: workspace_indexing_service
PURPOSE: Index hints for relational + semantic lookup — governance metadata (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_workspace_indexing_manifest() -> dict[str, Any]:
    return {
        "indices": [
            {"name": "ix_workflow_phase", "state_type": "workflow_state", "fields": ["workflow_id", "phase"]},
            {"name": "ix_contractor_tier", "state_type": "contractor_state", "fields": ["contractor_id", "compliance_tier"]},
        ],
        "full_text_optional": True,
        "mandatory_graph_dependency": False,
        "deterministic": True,
    }
