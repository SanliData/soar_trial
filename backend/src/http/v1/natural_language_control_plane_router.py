"""
ROUTER: natural_language_control_plane_router
PURPOSE: HTTP facade for NL command routing metadata (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.natural_language_control_plane.agent_task_dispatcher import recommend_dispatch
from src.natural_language_control_plane.command_audit_service import export_audit_log, record_command_audit
from src.natural_language_control_plane.human_approval_service import classify_approval_requirement
from src.natural_language_control_plane.nl_command_parser import parse_nl_command
from src.natural_language_control_plane.workflow_intent_router import route_workflow_intent

router = APIRouter(tags=["natural-language-control-plane"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "natural_language_control_plane_foundation": True,
        "unrestricted_nl_execution": False,
        "recommendation_only": True,
        "audit_required": True,
        "automatic_approval": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/nl-control/intents")
async def get_nl_intents() -> Dict[str, Any]:
    cmd = "Review this procurement bid and export a summary"
    parsed = parse_nl_command(cmd)
    routed = route_workflow_intent(parsed["parsed_intent"], parsed.get("workflow_scope"))
    dispatch = recommend_dispatch(cmd)
    return _envelope({"sample": {"parsed": parsed, "routed": routed, "dispatch": dispatch}})


@router.get("/system/nl-control/approval")
async def get_nl_approval() -> Dict[str, Any]:
    parsed = parse_nl_command("Submit this to the external portal")
    approval = classify_approval_requirement(parsed_intent=parsed["parsed_intent"], risk_level=parsed["risk_level"])
    return _envelope({"sample_approval": approval})


@router.get("/system/nl-control/audit")
async def get_nl_audit() -> Dict[str, Any]:
    parsed = parse_nl_command("Export an executive report")
    routed = route_workflow_intent(parsed["parsed_intent"], parsed.get("workflow_scope"))
    approval = classify_approval_requirement(parsed_intent=parsed["parsed_intent"], risk_level=parsed["risk_level"])
    record_command_audit(
        raw_command_summary=parsed["raw_command_summary"],
        parsed_intent=parsed["parsed_intent"],
        routed_workflow=routed["routed_workflow"],
        approval_required=approval["human_approval_required"],
        decision_status="pending",
    )
    return _envelope({"audit": export_audit_log(limit=25)})

