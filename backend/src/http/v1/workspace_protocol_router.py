"""
ROUTER: workspace_protocol_router
PURPOSE: HTTP facade for workspace protocol governance (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.workspace_protocol.agent_scope_service import export_agent_scopes_manifest
from src.workspace_protocol.permission_governance_service import export_permission_governance_manifest
from src.workspace_protocol.project_memory_service import export_project_memory_manifest
from src.workspace_protocol.runtime_rule_service import export_runtime_rules_manifest
from src.workspace_protocol.workspace_command_registry import export_workspace_commands_manifest
from src.workspace_protocol.workspace_policy_registry import export_workspace_policies_manifest
from src.workspace_protocol.workspace_skill_registry import export_workspace_skills_manifest

router = APIRouter(tags=["workspace-protocol"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "workspace_protocol_foundation": True,
        "unrestricted_persistent_memory": False,
        "autonomous_workspace_mutation": False,
        "uncontrolled_agent_spawning": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/workspaces/policies")
async def list_workspace_policies() -> Dict[str, Any]:
    return _envelope({"policies": export_workspace_policies_manifest()})


@router.get("/system/workspaces/rules")
async def list_runtime_rules() -> Dict[str, Any]:
    return _envelope({"rules": export_runtime_rules_manifest()})


@router.get("/system/workspaces/memory")
async def list_workspace_memory() -> Dict[str, Any]:
    return _envelope({"memory": export_project_memory_manifest()})


@router.get("/system/workspaces/commands")
async def list_workspace_commands() -> Dict[str, Any]:
    return _envelope({"commands": export_workspace_commands_manifest()})


@router.get("/system/workspaces/skills")
async def list_workspace_skills() -> Dict[str, Any]:
    return _envelope({"skills": export_workspace_skills_manifest()})


@router.get("/system/workspaces/permissions")
async def list_workspace_permissions() -> Dict[str, Any]:
    return _envelope(
        {
            "permission_governance": export_permission_governance_manifest(),
            "subagent_scopes": export_agent_scopes_manifest(),
        }
    )
