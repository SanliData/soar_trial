"""
ROUTER: long_context_runtime_router
PURPOSE: HTTP facade for long-context sparse governance (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.long_context_runtime.adaptive_context_loader import export_adaptive_context_loader_manifest
from src.long_context_runtime.context_partition_service import export_context_partition_manifest
from src.long_context_runtime.context_pressure_service import export_context_pressure_manifest
from src.long_context_runtime.retrieval_fallback_service import export_retrieval_fallback_manifest
from src.long_context_runtime.sparse_activation_service import export_sparse_provider_metadata_manifest

router = APIRouter(tags=["long-context-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "long_context_governance_foundation": True,
        "unrestricted_long_context_loading": False,
        "autonomous_context_mutation": False,
        "internet_scale_swarm_orchestration": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/context/pressure")
async def get_context_pressure() -> Dict[str, Any]:
    return _envelope(
        {
            "context_pressure": export_context_pressure_manifest(),
            "adaptive_loading": export_adaptive_context_loader_manifest(),
        }
    )


@router.get("/system/context/partitions")
async def get_context_partitions() -> Dict[str, Any]:
    return _envelope({"partitions": export_context_partition_manifest()})


@router.get("/system/context/sparse-providers")
async def get_sparse_providers() -> Dict[str, Any]:
    return _envelope({"sparse_providers": export_sparse_provider_metadata_manifest()})


@router.get("/system/context/fallbacks")
async def get_context_fallbacks() -> Dict[str, Any]:
    return _envelope({"fallbacks": export_retrieval_fallback_manifest()})
