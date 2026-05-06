"""
MODULE: latency_profile_service
PURPOSE: Deterministic latency classes (no fake benchmarks) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_latency_profiles() -> dict[str, Any]:
    rows = [
        {
            "profile_id": "latency:orchestration",
            "expected_latency": "moderate",
            "inference_pattern": "none",
            "orchestration_delay": "low",
            "retrieval_delay": "moderate",
            "context_expansion_delay": "moderate",
            "no_fake_benchmark_claims": True,
            "deterministic": True,
        },
        {
            "profile_id": "latency:low_latency_inference",
            "expected_latency": "low",
            "inference_pattern": "decode_sensitive",
            "orchestration_delay": "low",
            "retrieval_delay": "low",
            "context_expansion_delay": "low",
            "no_fake_benchmark_claims": True,
            "deterministic": True,
        },
        {
            "profile_id": "latency:batch_inference",
            "expected_latency": "low_for_batch",
            "inference_pattern": "batched",
            "orchestration_delay": "moderate",
            "retrieval_delay": "low",
            "context_expansion_delay": "moderate",
            "no_fake_benchmark_claims": True,
            "deterministic": True,
        },
    ]
    return {"latency_profiles": rows, "deterministic": True}

