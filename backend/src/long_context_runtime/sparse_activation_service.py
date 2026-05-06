"""
MODULE: sparse_activation_service
PURPOSE: Sparse inference metadata — no provider orchestration mutation (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_SPARSE_PROVIDER_ROWS: list[dict[str, Any]] = [
    {
        "provider_name": "openai",
        "total_parameters": 1_760_000_000_000,
        "active_parameters": 44_000_000_000,
        "sparse_moe": True,
        "sparse_moe_enabled": True,
        "context_efficiency_score": 0.82,
        "reasoning_profile": "dense_aux_routing",
    },
    {
        "provider_name": "anthropic",
        "total_parameters": None,
        "active_parameters": None,
        "sparse_moe": False,
        "sparse_moe_enabled": False,
        "context_efficiency_score": 0.79,
        "reasoning_profile": "long_context_dense",
    },
    {
        "provider_name": "local_llm",
        "total_parameters": 8_000_000_000,
        "active_parameters": 8_000_000_000,
        "sparse_moe": False,
        "sparse_moe_enabled": False,
        "context_efficiency_score": 0.71,
        "reasoning_profile": "single_expert",
    },
]


def export_sparse_provider_metadata_manifest() -> dict[str, Any]:
    return {
        "providers": [dict(r) for r in _SPARSE_PROVIDER_ROWS],
        "metadata_only": True,
        "direct_provider_orchestration_mutation": False,
        "deterministic": True,
    }
