"""
MODULE: hardware_validation_service
PURPOSE: Validation for hardware metadata (no fake benchmarks) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def reject_fake_benchmarks(payload: dict[str, Any]) -> None:
    if payload.get("fake_benchmark_claims") is True:
        raise ValueError("fake benchmark claims rejected")


def validate_hardware_kind(kind: str) -> None:
    if (kind or "").strip() not in {"CPU", "GPU", "TPU", "NPU", "LPU"}:
        raise ValueError("invalid hardware kind")

