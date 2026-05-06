"""
MODULE: agent_os_validation_service
PURPOSE: Validate agent OS registry and reject unsafe mutation/execution flags (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_no_uncontrolled_agent_fleet_flags(flags: dict[str, Any] | None) -> None:
    if not flags:
        return
    if flags.get("autonomous_agent_spawning") is True:
        raise ValueError("autonomous agent spawning rejected")
    if flags.get("autonomous_fleet_mutation") is True:
        raise ValueError("autonomous fleet mutation rejected")
    if flags.get("unrestricted_nl_execution") is True:
        raise ValueError("unrestricted natural-language execution rejected")
    if flags.get("hidden_execution_permissions") is True:
        raise ValueError("hidden execution permissions rejected")


def validate_agent_record(agent: dict[str, Any]) -> None:
    if not isinstance(agent, dict):
        raise ValueError("invalid agent record")
    required = {
        "agent_id",
        "agent_name",
        "agent_role",
        "workflow_scope",
        "allowed_capabilities",
        "permission_scope",
        "status",
        "human_approval_required",
        "created_at",
        "tags",
    }
    if required - agent.keys():
        raise ValueError("agent record missing required fields")
    for k in ("agent_id", "agent_name", "agent_role", "workflow_scope", "permission_scope", "status", "created_at"):
        if not isinstance(agent.get(k), str) or not agent[k].strip():
            raise ValueError(f"invalid {k}")
    if not isinstance(agent.get("allowed_capabilities"), list) or not all(
        isinstance(x, str) and x.strip() for x in agent["allowed_capabilities"]
    ):
        raise ValueError("invalid allowed_capabilities")
    if not isinstance(agent.get("human_approval_required"), bool):
        raise ValueError("invalid human_approval_required")
    if not isinstance(agent.get("tags"), list) or not all(isinstance(x, str) for x in agent["tags"]):
        raise ValueError("invalid tags")

