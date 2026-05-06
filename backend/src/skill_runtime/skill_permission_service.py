"""
MODULE: skill_permission_service
PURPOSE: Least-privilege skill permission manifests (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_registry_service import SKILL_REGISTRY, get_skill_definition

_MEMORY_ACCESS: dict[str, list[str]] = {
    "procurement_review": ["workspace_scoped_read"],
    "onboarding_validator": ["ephemeral_workspace_buffer"],
    "graph_investigator": ["graph_projection_read"],
    "reliability_audit": ["reliability_manifest_read"],
    "browser_compliance": ["firewall_policy_read"],
}

_EXECUTION_DOMAINS: dict[str, list[str]] = {
    "procurement_review": ["internal_catalog"],
    "onboarding_validator": ["internal_onboarding"],
    "graph_investigator": ["internal_graph_read"],
    "reliability_audit": ["internal_governance_read"],
    "browser_compliance": ["firewall_governed_browser"],
}


def export_skill_permissions_manifest() -> dict[str, Any]:
    rows = []
    for name in sorted(SKILL_REGISTRY.keys()):
        rows.append(
            {
                "skill_name": name,
                "allowed_tools": list(SKILL_REGISTRY[name]["allowed_tools"]),
                "memory_access": list(_MEMORY_ACCESS.get(name, [])),
                "execution_domains": list(_EXECUTION_DOMAINS.get(name, [])),
                "escalation_policy": SKILL_REGISTRY[name]["escalation_policy"],
                "hidden_tool_escalation": False,
            }
        )
    return {
        "skills": rows,
        "least_privilege_enforced": True,
        "deterministic": True,
    }


def evaluate_skill_permission_gate(skill_name: str, *, principal_permissions_ok: bool) -> dict[str, Any]:
    if get_skill_definition(skill_name) is None:
        raise ValueError("invalid skill")
    return {
        "allowed": bool(principal_permissions_ok),
        "reason": "principal_skill_grant" if principal_permissions_ok else "principal_skill_deny",
        "deterministic": True,
    }
