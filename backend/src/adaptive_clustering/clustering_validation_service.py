"""
MODULE: clustering_validation_service
PURPOSE: Validation for clustering metadata-only foundations (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def reject_uncontrolled_optimization(payload: dict[str, Any]) -> None:
    if payload.get("autonomous_runtime_mutation") is True:
        raise ValueError("autonomous runtime mutation rejected")
    if payload.get("self_optimizing_live_clustering") is True:
        raise ValueError("self optimizing live clustering rejected")


def validate_score01(x: float) -> None:
    if float(x) < 0.0 or float(x) > 1.0:
        raise ValueError("score must be in [0,1]")

