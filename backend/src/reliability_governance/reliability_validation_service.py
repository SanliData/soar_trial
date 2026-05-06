"""
MODULE: reliability_validation_service
PURPOSE: Validate governance metrics and trace shapes (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_ratio(name: str, value: float) -> float:
    v = float(value)
    if v < 0.0 or v > 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return v


def validate_trace_shape(obj: dict[str, Any]) -> None:
    required = ("category", "severity", "detail")
    for r in required:
        if r not in obj:
            raise ValueError(f"trace missing field: {r}")
    if obj["severity"] not in ("low", "medium", "high", "critical"):
        raise ValueError("invalid trace severity")
