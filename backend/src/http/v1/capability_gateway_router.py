"""
ROUTER: capability_gateway_router
PURPOSE: HTTP facade for capability gateway governance (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.capability_gateway.browser_automation_policy_service import export_browser_automation_policies
from src.capability_gateway.capability_execution_policy import export_execution_policies
from src.capability_gateway.external_tool_governance_service import export_external_tool_governance
from src.capability_gateway.hybrid_serving_service import export_hybrid_serving_metadata
from src.capability_gateway.local_inference_service import export_local_inference_metadata
from src.capability_gateway.mcp_gateway_registry import export_gateways_manifest
from src.capability_gateway.provider_abstraction_service import export_providers_surfaces

router = APIRouter(tags=["capability-gateway"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "capability_gateway_foundation": True,
        "unrestricted_external_execution": False,
        "autonomous_internet_orchestration": False,
        "unrestricted_tool_chaining": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/gateways")
async def list_gateways() -> Dict[str, Any]:
    return _envelope({"gateways": export_gateways_manifest()})


@router.get("/system/providers")
async def list_providers() -> Dict[str, Any]:
    return _envelope({"providers": export_providers_surfaces()})


@router.get("/system/execution-policies")
async def list_execution_policies() -> Dict[str, Any]:
    return _envelope({"execution_policies": export_execution_policies()})


@router.get("/system/local-inference")
async def get_local_inference() -> Dict[str, Any]:
    return _envelope({"local_inference": export_local_inference_metadata()})


@router.get("/system/browser-policies")
async def list_browser_policies() -> Dict[str, Any]:
    return _envelope({"browser_policies": export_browser_automation_policies()})


@router.get("/system/hybrid-serving")
async def get_hybrid_serving() -> Dict[str, Any]:
    return _envelope({"hybrid_serving": export_hybrid_serving_metadata()})
