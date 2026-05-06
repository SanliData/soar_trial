"""
MODULE: approval_validation_service
PURPOSE: Validation for approval lineage and transitions (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def require_approval_lineage(event: dict[str, Any]) -> None:
    lineage = event.get("approval_lineage")
    if not isinstance(lineage, dict) or not lineage.get("workflow_id") or not lineage.get("checkpoint_id"):
        raise ValueError("approval lineage required")


def reject_auto_approval(event: dict[str, Any]) -> None:
    if event.get("automatic_approval") is True:
        raise ValueError("automatic approval rejected")

