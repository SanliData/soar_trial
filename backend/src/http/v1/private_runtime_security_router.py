"""
ROUTER: private_runtime_security_router
PURPOSE: HTTP facade for private runtime isolation (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.private_runtime_security.execution_boundary_service import export_execution_boundary_manifest
from src.private_runtime_security.network_exposure_service import export_network_exposure_manifest
from src.private_runtime_security.non_root_execution_service import export_non_root_execution_manifest
from src.private_runtime_security.private_mesh_policy_service import export_private_mesh_policy_manifest
from src.private_runtime_security.runtime_isolation_service import export_runtime_isolation_manifest
from src.private_runtime_security.tailscale_policy_service import export_tailscale_policy_manifest

router = APIRouter(tags=["private-runtime-security"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "private_runtime_security_foundation": True,
        "public_runtime_exposure_default": False,
        "ai_runtime_publicly_exposed": False,
        "unrestricted_network_egress_default": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/runtime/isolation")
async def get_runtime_isolation() -> Dict[str, Any]:
    return _envelope(
        {
            "isolation": export_runtime_isolation_manifest(),
            "execution_boundaries": export_execution_boundary_manifest(),
        }
    )


@router.get("/system/runtime/network-exposure")
async def get_network_exposure() -> Dict[str, Any]:
    return _envelope({"network_exposure": export_network_exposure_manifest()})


@router.get("/system/runtime/private-mesh")
async def get_private_mesh() -> Dict[str, Any]:
    return _envelope(
        {
            "private_mesh": export_private_mesh_policy_manifest(),
            "tailscale": export_tailscale_policy_manifest(),
        }
    )


@router.get("/system/runtime/non-root")
async def get_non_root() -> Dict[str, Any]:
    return _envelope({"non_root": export_non_root_execution_manifest()})
