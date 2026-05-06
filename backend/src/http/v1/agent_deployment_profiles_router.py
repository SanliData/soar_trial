"""
ROUTER: agent_deployment_profiles_router
PURPOSE: Governed deployment profile facade (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.agent_deployment_profiles.channel_integration_policy import export_channel_policies
from src.agent_deployment_profiles.deployment_profile_registry import export_deployment_profiles
from src.agent_deployment_profiles.deployment_safety_service import export_deployment_safety
from src.agent_deployment_profiles.private_runtime_profile_service import export_private_runtime_requirements

router = APIRouter(prefix="/system/deployment", tags=["agent-deployment-profiles"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "deployment_profile_foundation": True,
        "no_live_deployment_execution": True,
        "no_public_agent_exposure": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/profiles")
async def get_profiles() -> Dict[str, Any]:
    return _envelope(export_deployment_profiles())


@router.get("/channels")
async def get_channels() -> Dict[str, Any]:
    return _envelope(export_channel_policies())


@router.get("/private-runtime")
async def get_private_runtime() -> Dict[str, Any]:
    return _envelope(export_private_runtime_requirements())


@router.get("/safety")
async def get_safety() -> Dict[str, Any]:
    return _envelope(export_deployment_safety())

