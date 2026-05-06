"""
MODULE: persistent_workflow_service
PURPOSE: Durable workflow identifiers and phases — metadata (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_persistent_workflow_manifest() -> dict[str, Any]:
    return {
        "workflows": [
            {
                "workflow_key": "municipal_permit_tracking",
                "persistence_scope": "tenant_bound",
                "checkpoint_strategy": "phase_boundary_only",
                "graph_augmentation_optional": True,
            },
            {
                "workflow_key": "contractor_compliance_review",
                "persistence_scope": "project_bound",
                "checkpoint_strategy": "human_gate_or_daily",
                "graph_augmentation_optional": True,
            },
        ],
        "deterministic": True,
    }
