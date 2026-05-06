"""
MODULE: dynamic_skill_loader
PURPOSE: Scoped skill load planning — no global preload (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_dependency_service import validate_dependency_closure
from src.skill_runtime.skill_permission_service import evaluate_skill_permission_gate
from src.skill_runtime.skill_registry_service import get_skill_definition


def plan_skill_load(
    skill_name: str,
    *,
    activation_intent: str,
    runtime_scope: str,
    principal_permissions_ok: bool,
) -> dict[str, Any]:
    """Deterministic load plan metadata — does not mutate runtime."""
    definition = get_skill_definition(skill_name)
    if definition is None:
        raise ValueError("invalid skill")

    intents_allowed = frozenset(
        {"automatic_intent_match", "explicit_command", "workflow_trigger", "evaluation_trigger"}
    )
    if activation_intent.strip() not in intents_allowed:
        raise ValueError("invalid activation intent")

    scope_ok = definition["runtime_scope"] == runtime_scope.strip()
    perm = evaluate_skill_permission_gate(skill_name, principal_permissions_ok=principal_permissions_ok)

    deps_ok = True
    dep_detail: str | None = None
    try:
        validate_dependency_closure(skill_name)
    except ValueError as exc:
        deps_ok = False
        dep_detail = str(exc)

    load_allowed = (
        scope_ok
        and perm["allowed"]
        and deps_ok
        and activation_intent.strip() in definition["activation_rules"]
    )

    return {
        "skill_name": skill_name,
        "scoped_loading_only": True,
        "global_preload": False,
        "load_allowed": load_allowed,
        "scope_match": scope_ok,
        "permission_gate": perm,
        "dependency_valid": deps_ok,
        "dependency_error": dep_detail,
        "activation_intent_ok": activation_intent.strip() in definition["activation_rules"],
        "deterministic": True,
    }
