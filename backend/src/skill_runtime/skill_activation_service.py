"""
MODULE: skill_activation_service
PURPOSE: Governed activation methods — auditable, no hidden activation (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_registry_service import SKILL_REGISTRY, get_skill_definition

_ACTIVATION_METHODS = frozenset(
    {"automatic_intent_match", "explicit_command", "workflow_trigger", "evaluation_trigger"}
)


def export_skill_activation_manifest() -> dict[str, Any]:
    rows = []
    for name in sorted(SKILL_REGISTRY.keys()):
        rows.append(
            {
                "skill_name": name,
                "supported_methods": list(SKILL_REGISTRY[name]["activation_rules"]),
                "hidden_activation": False,
                "autonomous_spawning": False,
            }
        )
    return {
        "skills": rows,
        "allowed_methods_global": sorted(_ACTIVATION_METHODS),
        "deterministic": True,
    }


def export_active_skills_view() -> dict[str, Any]:
    """
    Read-only activation surface — no live session state in foundation.
    """
    return {
        "live_session_skills": [],
        "activation_surface": "governed_read_manifest_v1",
        "eligible_under_explicit_command": sorted(SKILL_REGISTRY.keys()),
        "unrestricted_autonomous_activation": False,
        "hidden_activation_paths": False,
        "deterministic": True,
    }


def describe_activation_trace(skill_name: str, method: str) -> dict[str, Any]:
    if get_skill_definition(skill_name) is None:
        raise ValueError("invalid skill")
    if method.strip() not in _ACTIVATION_METHODS:
        raise ValueError("invalid activation method")
    allowed = method.strip() in SKILL_REGISTRY[skill_name]["activation_rules"]
    return {
        "skill_name": skill_name,
        "method": method,
        "would_activate": allowed,
        "auditable": True,
        "deterministic": True,
    }
