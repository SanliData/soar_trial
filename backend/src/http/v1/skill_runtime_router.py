"""
ROUTER: skill_runtime_router
PURPOSE: HTTP facade for governed skill runtime manifests (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.skill_runtime.skill_activation_service import export_active_skills_view
from src.skill_runtime.skill_context_optimizer import export_context_optimization_manifest
from src.skill_runtime.skill_dependency_service import export_skill_dependencies_manifest
from src.skill_runtime.skill_execution_trace_service import export_skill_execution_traces
from src.skill_runtime.skill_permission_service import export_skill_permissions_manifest
from src.skill_runtime.skill_registry_service import export_skill_registry_manifest

router = APIRouter(tags=["skill-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "skill_runtime_foundation": True,
        "unrestricted_skill_spawning": False,
        "recursive_workflow_mutation": False,
        "hidden_tool_escalation": False,
        "uncontrolled_skill_inheritance": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/skills")
async def list_skills() -> Dict[str, Any]:
    return _envelope({"skills": export_skill_registry_manifest()})


@router.get("/system/skills/active")
async def list_active_skills() -> Dict[str, Any]:
    return _envelope({"active": export_active_skills_view()})


@router.get("/system/skills/permissions")
async def list_skill_permissions() -> Dict[str, Any]:
    return _envelope({"permissions": export_skill_permissions_manifest()})


@router.get("/system/skills/dependencies")
async def list_skill_dependencies() -> Dict[str, Any]:
    return _envelope({"dependencies": export_skill_dependencies_manifest()})


@router.get("/system/skills/context-optimization")
async def list_context_optimization() -> Dict[str, Any]:
    return _envelope({"context_optimization": export_context_optimization_manifest()})


@router.get("/system/skills/traces")
async def list_skill_traces() -> Dict[str, Any]:
    return _envelope({"traces": export_skill_execution_traces()})
