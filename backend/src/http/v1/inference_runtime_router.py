"""
ROUTER: inference_runtime_router
PURPOSE: HTTP facade for inference runtime governance manifests (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.inference_runtime.continuous_batching_service import export_continuous_batching_manifest
from src.inference_runtime.inference_cost_governance_service import export_inference_cost_manifest
from src.inference_runtime.kv_cache_registry import export_kv_cache_registry_manifest
from src.inference_runtime.prefill_decode_optimizer import export_prefill_decode_guidance_manifest
from src.inference_runtime.prefill_pressure_service import export_prefill_pressure_manifest
from src.inference_runtime.runtime_collapse_detection_service import export_collapse_detection_manifest
from src.inference_runtime.runtime_efficiency_service import export_runtime_efficiency_manifest
from src.inference_runtime.runtime_parallelism_service import export_runtime_parallelism_manifest
from src.inference_runtime.runtime_telemetry_service import export_runtime_telemetry_manifest
from src.inference_runtime.runtime_token_budget_service import export_runtime_token_budgets_manifest
from src.inference_runtime.speculative_execution_service import export_speculative_execution_manifest

router = APIRouter(tags=["inference-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "inference_runtime_governance_foundation": True,
        "uncontrolled_runtime_expansion": False,
        "autonomous_runtime_scheduling": False,
        "recursive_runtime_orchestration": False,
        "self_tuning_runtime": False,
        "execution_auto_mutation": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/inference/kv-cache")
async def get_kv_cache() -> Dict[str, Any]:
    return _envelope({"kv_cache": export_kv_cache_registry_manifest()})


@router.get("/system/inference/batching")
async def get_batching() -> Dict[str, Any]:
    return _envelope({"batching": export_continuous_batching_manifest()})


@router.get("/system/inference/token-budgets")
async def get_token_budgets() -> Dict[str, Any]:
    return _envelope({"token_budgets": export_runtime_token_budgets_manifest()})


@router.get("/system/inference/costs")
async def get_inference_costs() -> Dict[str, Any]:
    return _envelope({"costs": export_inference_cost_manifest()})


@router.get("/system/inference/parallelism")
async def get_parallelism() -> Dict[str, Any]:
    return _envelope({"parallelism": export_runtime_parallelism_manifest()})


@router.get("/system/inference/speculative")
async def get_speculative() -> Dict[str, Any]:
    return _envelope({"speculative": export_speculative_execution_manifest()})


@router.get("/system/inference/telemetry")
async def get_telemetry() -> Dict[str, Any]:
    return _envelope({"telemetry": export_runtime_telemetry_manifest()})


@router.get("/system/inference/collapse-risk")
async def get_collapse_risk() -> Dict[str, Any]:
    return _envelope({"collapse_risk": export_collapse_detection_manifest()})


@router.get("/system/inference/prefill-pressure")
async def get_prefill_pressure() -> Dict[str, Any]:
    return _envelope({"prefill_pressure": export_prefill_pressure_manifest()})


@router.get("/system/inference/efficiency")
async def get_efficiency() -> Dict[str, Any]:
    merged = {
        "efficiency": export_runtime_efficiency_manifest(),
        "prefill_decode_guidance": export_prefill_decode_guidance_manifest(),
    }
    return _envelope(merged)
