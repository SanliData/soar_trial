"""
MODULE: inference_acceleration_service
PURPOSE: Inference acceleration capability metadata (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_inference_acceleration() -> dict[str, Any]:
    rows = [
        {
            "hardware_kind": "CPU",
            "sparse_inference_support": "limited",
            "batching_support": "medium",
            "low_latency_suitability": "medium",
            "memory_efficiency": "high",
            "parallel_inference_suitability": "medium",
            "deterministic": True,
        },
        {
            "hardware_kind": "GPU",
            "sparse_inference_support": "medium",
            "batching_support": "high",
            "low_latency_suitability": "medium",
            "memory_efficiency": "medium",
            "parallel_inference_suitability": "high",
            "deterministic": True,
        },
        {
            "hardware_kind": "LPU",
            "sparse_inference_support": "medium",
            "batching_support": "high",
            "low_latency_suitability": "high",
            "memory_efficiency": "high",
            "parallel_inference_suitability": "high",
            "deterministic": True,
        },
    ]
    return {"inference_acceleration": rows, "deterministic": True, "metadata_only": True}

