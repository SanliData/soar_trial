"""
MODULE: h043_inference_hooks
PURPOSE: Bridges long-context governance into inference manifests (H-043 + H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.long_context_runtime.adaptive_context_loader import export_adaptive_context_loader_manifest
from src.long_context_runtime.context_pressure_service import classify_context_pressure
from src.long_context_runtime.sparse_activation_service import export_sparse_provider_metadata_manifest


def export_inference_governance_addon() -> dict[str, Any]:
    """
    Embeddable in inference telemetry envelope — explains hooks without mutating execution.
    """
    sample_pressure = classify_context_pressure(
        {
            "context_window_tokens": 22000,
            "retrieval_doc_breadth": 10,
            "duplicated_blocks": 3,
            "reflection_share": 0.14,
            "orchestration_depth_hint": 4,
        }
    )
    return {
        "schema": "h043_inference_bridge_v1",
        "long_context_telemetry_hooks": {
            "adaptive_loading_manifest_id": export_adaptive_context_loader_manifest().get(
                "loading_policy", ""
            ),
            "context_pressure_sample": sample_pressure["pressure_level"],
            "sparse_runtime_metadata_registered": True,
        },
        "prefill_amplification_cross_check": True,
        "deterministic": True,
    }


def export_ensemble_budget_cross_hint() -> dict[str, Any]:
    return {"ensemble_evaluation_budget_linked": True, "no_hidden_evaluator_weights": True, "deterministic": True}


def trimmed_sparse_providers_for_inference() -> dict[str, Any]:
    sparse = export_sparse_provider_metadata_manifest()
    return {"provider_rows_count": len(sparse.get("providers", [])), "metadata_only": True, "deterministic": True}

