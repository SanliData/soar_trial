"""
MODULE: hybrid_serving_service
PURPOSE: Hybrid AI serving abstraction — no infra rewrite (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_SURFACES: list[dict[str, Any]] = [
    {
        "surface_id": "hosted_managed",
        "mode": "hosted_inference",
        "routing_hint": "vendor_api_with_policy_headers",
        "future_vllm_compatible": False,
    },
    {
        "surface_id": "local_loopback",
        "mode": "local_inference",
        "routing_hint": "ollama_or_local_bundle",
        "future_vllm_compatible": False,
    },
    {
        "surface_id": "reserved_internal_vllm",
        "mode": "future_vllm",
        "routing_hint": "internal_lb_placeholder",
        "future_vllm_compatible": True,
    },
]


def export_hybrid_serving_metadata() -> dict[str, Any]:
    return {
        "surfaces": list(_SURFACES),
        "abstraction_only": True,
        "distributed_cluster_rewrite": False,
        "deterministic": True,
    }
