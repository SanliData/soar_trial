"""
MODULE: agent_command_center
PURPOSE: Command center metadata (recommendations only) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.natural_language_control_plane.nl_command_parser import parse_nl_command
from src.natural_language_control_plane.workflow_intent_router import route_workflow_intent
from src.natural_language_control_plane.human_approval_service import classify_approval_requirement


def build_command_center_manifest(raw_command: str) -> dict[str, Any]:
    parsed = parse_nl_command(raw_command)
    routed = route_workflow_intent(parsed["parsed_intent"], parsed.get("workflow_scope"))
    approval = classify_approval_requirement(
        parsed_intent=parsed["parsed_intent"],
        risk_level=parsed["risk_level"],
    )
    return {
        "command_intake": {"raw_command_summary": parsed["raw_command_summary"]},
        "intent": parsed,
        "routed_workflow": routed,
        "approval": approval,
        "dispatch_recommendation": {
            "target_agent_type": parsed.get("target_agent_type"),
            "recommendation_only": True,
            "no_direct_execution": True,
        },
        "audit_trail_linkage": {"audit_required": True, "command_id_placeholder": "cmd-placeholder"},
        "deterministic": True,
    }

