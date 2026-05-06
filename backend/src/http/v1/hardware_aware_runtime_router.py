"""
ROUTER: hardware_aware_runtime_router
PURPOSE: Hardware-aware runtime metadata facade (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.hardware_aware_runtime.hardware_cost_service import export_hardware_costs
from src.hardware_aware_runtime.hardware_profile_service import export_hardware_profiles
from src.hardware_aware_runtime.inference_acceleration_service import export_inference_acceleration
from src.hardware_aware_runtime.latency_profile_service import export_latency_profiles
from src.hardware_aware_runtime.runtime_hardware_router import export_hardware_routing

router = APIRouter(prefix="/system/runtime", tags=["hardware-aware-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "hardware_aware_runtime_foundation": True,
        "recommendation_only": True,
        "no_infrastructure_execution": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/hardware-profiles")
async def get_profiles() -> Dict[str, Any]:
    return _envelope(export_hardware_profiles())


@router.get("/hardware-routing")
async def get_routing() -> Dict[str, Any]:
    return _envelope(export_hardware_routing())


@router.get("/hardware-costs")
async def get_costs() -> Dict[str, Any]:
    return _envelope(export_hardware_costs())


@router.get("/latency-profiles")
async def get_latency() -> Dict[str, Any]:
    return _envelope(export_latency_profiles())


@router.get("/inference-acceleration")
async def get_acceleration() -> Dict[str, Any]:
    return _envelope(export_inference_acceleration())

