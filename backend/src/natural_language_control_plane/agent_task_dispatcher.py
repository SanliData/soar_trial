"""
MODULE: agent_task_dispatcher
PURPOSE: Dispatch recommendations based on parsed intent (no execution) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import get_agent
from src.natural_language_control_plane.nl_command_parser import parse_nl_command


def recommend_dispatch(raw_command: str) -> dict[str, Any]:
    parsed = parse_nl_command(raw_command)
    target = parsed.get("target_agent_type")
    agent = None
    if target:
        try:
            agent = get_agent(target)
        except ValueError:
            agent = None
    return {
        "intent": parsed,
        "recommended_agent": agent,
        "recommendation_only": True,
        "no_direct_execution": True,
        "deterministic": True,
    }

