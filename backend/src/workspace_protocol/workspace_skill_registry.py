"""
MODULE: workspace_skill_registry
PURPOSE: Reusable operational skills — deterministic activation manifests (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

WORKSPACE_SKILL_EPOCH = "2025-05-01T00:00:00Z"

_WORKSPACE_SKILLS: dict[str, dict[str, Any]] = {
    "procurement_review": {
        "skill_id": "procurement_review",
        "skill_type": "procurement_review",
        "activation": "explicit_operator_invoke",
        "unrestricted_orchestration": False,
        "deterministic_package": True,
        "created_at": WORKSPACE_SKILL_EPOCH,
    },
    "graph_investigation": {
        "skill_id": "graph_investigation",
        "skill_type": "graph_investigation",
        "activation": "explicit_operator_invoke",
        "unrestricted_orchestration": False,
        "deterministic_package": True,
        "created_at": WORKSPACE_SKILL_EPOCH,
    },
    "onboarding_validation": {
        "skill_id": "onboarding_validation",
        "skill_type": "onboarding_validation",
        "activation": "explicit_operator_invoke",
        "unrestricted_orchestration": False,
        "deterministic_package": True,
        "created_at": WORKSPACE_SKILL_EPOCH,
    },
    "reliability_audit": {
        "skill_id": "reliability_audit",
        "skill_type": "reliability_audit",
        "activation": "explicit_operator_invoke",
        "unrestricted_orchestration": False,
        "deterministic_package": True,
        "created_at": WORKSPACE_SKILL_EPOCH,
    },
    "compliance_review": {
        "skill_id": "compliance_review",
        "skill_type": "compliance_review",
        "activation": "explicit_human_gate_plus_operator",
        "unrestricted_orchestration": False,
        "deterministic_package": True,
        "created_at": WORKSPACE_SKILL_EPOCH,
    },
}


def export_workspace_skills_manifest() -> list[dict[str, Any]]:
    return [dict(_WORKSPACE_SKILLS[k]) for k in sorted(_WORKSPACE_SKILLS.keys())]
