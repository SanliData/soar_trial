"""
ROUTER: agui_runtime_router
PURPOSE: AG-UI event streaming facade (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.agui_runtime.event_stream_service import export_event_stream
from src.agui_runtime.human_approval_stream import export_approval_stream
from src.agui_runtime.tool_call_stream_service import export_tool_streams
from src.agui_runtime.workflow_event_bus import export_workflow_bus

router = APIRouter(prefix="/system/agui", tags=["agui-runtime"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "agui_runtime_foundation": True,
        "event_metadata_only": True,
        "no_unrestricted_live_execution": True,
        "deterministic": True,
        "auditable": True,
    }
    out.update(payload)
    return out


@router.get("/events")
async def get_events() -> Dict[str, Any]:
    return _envelope(export_event_stream(workflow_id="wf-demo-001"))


@router.get("/workflows")
async def get_workflows() -> Dict[str, Any]:
    return _envelope(export_workflow_bus(workflow_id="wf-demo-001", limit=80))


@router.get("/tool-streams")
async def get_tool_streams() -> Dict[str, Any]:
    return _envelope(export_tool_streams())


@router.get("/approval-stream")
async def get_approval_stream() -> Dict[str, Any]:
    return _envelope(export_approval_stream())


