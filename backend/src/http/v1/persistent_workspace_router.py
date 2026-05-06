"""
ROUTER: persistent_workspace_router
PURPOSE: HTTP facade for governed persistent workspace (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.persistent_workspace.cross_session_context_service import export_cross_session_context_manifest
from src.persistent_workspace.persistent_workflow_service import export_persistent_workflow_manifest
from src.persistent_workspace.scheduled_execution_service import export_scheduled_execution_manifest
from src.persistent_workspace.state_snapshot_service import export_state_snapshot_manifest
from src.persistent_workspace.workspace_indexing_service import export_workspace_indexing_manifest
from src.persistent_workspace.workspace_state_service import export_workspace_state_manifest

router = APIRouter(tags=["persistent-workspace"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "persistent_workspace_foundation": True,
        "uncontrolled_persistent_execution": False,
        "autonomous_agent_swarms": False,
        "recursive_memory_expansion": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/workspace/state")
async def get_workspace_state() -> Dict[str, Any]:
    return _envelope(
        {
            "workspace_state": export_workspace_state_manifest(),
            "cross_session": export_cross_session_context_manifest(),
            "persistent_workflows": export_persistent_workflow_manifest(),
            "snapshots": export_state_snapshot_manifest(),
            "indexing": export_workspace_indexing_manifest(),
        }
    )


@router.get("/system/workspace/schedules")
async def get_workspace_schedules() -> Dict[str, Any]:
    return _envelope({"schedules": export_scheduled_execution_manifest()})
