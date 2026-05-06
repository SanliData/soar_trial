"""
MODULE: runtime_hardware_router
PURPOSE: Workload -> hardware recommendation mapping (recommendation only) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


WORKLOADS = {
    "graph_traversal",
    "retrieval",
    "embeddings",
    "low_latency_inference",
    "batch_inference",
    "evaluation",
    "orchestration",
}


def route_workload(*, workload: str) -> dict[str, Any]:
    w = (workload or "").strip()
    if w not in WORKLOADS:
        raise ValueError("unknown workload")

    if w in {"orchestration", "retrieval", "evaluation", "graph_traversal"}:
        hw = "CPU"
        latency = "moderate"
        reason = "control-plane / IO heavy workloads"
    elif w == "embeddings":
        hw = "GPU"
        latency = "low_for_batch"
        reason = "matrix-heavy embedding throughput"
    elif w == "batch_inference":
        hw = "GPU"
        latency = "low_for_batch"
        reason = "throughput-optimized"
    else:
        hw = "LPU"
        latency = "very_low_decode"
        reason = "decode-sensitive low latency"

    return {
        "workload": w,
        "recommended_hardware": hw,
        "latency_expectation": latency,
        "efficiency_reasoning": reason,
        "recommendation_only": True,
        "deterministic": True,
    }


def export_hardware_routing() -> dict[str, Any]:
    rows = [route_workload(workload=w) for w in sorted(WORKLOADS)]
    return {"hardware_routing": rows, "deterministic": True}

