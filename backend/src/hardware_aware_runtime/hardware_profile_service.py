"""
MODULE: hardware_profile_service
PURPOSE: Hardware profile metadata (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.hardware_aware_runtime.hardware_validation_service import validate_hardware_kind


def export_hardware_profiles() -> dict[str, Any]:
    profiles = [
        {
            "hardware_kind": "CPU",
            "parallelism_level": "medium",
            "memory_model": "shared_ram",
            "latency_profile": "moderate",
            "power_efficiency": "high",
            "workload_strength": ["orchestration", "retrieval", "evaluation"],
            "orchestration_notes": "good for control-plane and IO-bound tasks",
            "deterministic": True,
        },
        {
            "hardware_kind": "GPU",
            "parallelism_level": "high",
            "memory_model": "hbm_vram",
            "latency_profile": "low_for_batch",
            "power_efficiency": "medium",
            "workload_strength": ["embeddings", "batch_inference"],
            "orchestration_notes": "best for throughput; may not be lowest p50 latency",
            "deterministic": True,
        },
        {
            "hardware_kind": "TPU",
            "parallelism_level": "high",
            "memory_model": "tpu_hbm",
            "latency_profile": "low_for_matmul",
            "power_efficiency": "high",
            "workload_strength": ["batch_inference", "embeddings"],
            "orchestration_notes": "specialized acceleration; metadata only in foundation",
            "deterministic": True,
        },
        {
            "hardware_kind": "NPU",
            "parallelism_level": "medium",
            "memory_model": "on_die",
            "latency_profile": "low_for_edge",
            "power_efficiency": "high",
            "workload_strength": ["low_latency_inference"],
            "orchestration_notes": "edge-style low latency; metadata only",
            "deterministic": True,
        },
        {
            "hardware_kind": "LPU",
            "parallelism_level": "high",
            "memory_model": "streaming",
            "latency_profile": "very_low_decode",
            "power_efficiency": "high",
            "workload_strength": ["low_latency_inference"],
            "orchestration_notes": "decode-optimized; no real orchestration in foundation",
            "deterministic": True,
        },
    ]
    for p in profiles:
        validate_hardware_kind(p["hardware_kind"])
    return {"hardware_profiles": profiles, "deterministic": True, "metadata_only": True}

