"""
MODULE: skill_dependency_service
PURPOSE: Acyclic skill dependencies — no recursive expansion (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.skill_runtime.skill_registry_service import SKILL_REGISTRY, get_skill_definition


def export_skill_dependencies_manifest() -> dict[str, Any]:
    edges = []
    for name in sorted(SKILL_REGISTRY.keys()):
        for dep in SKILL_REGISTRY[name]["dependency_skills"]:
            edges.append({"from_skill": name, "to_skill": dep, "inheritance_type": "requires_loaded"})
    return {
        "edges": edges,
        "unrestricted_dependency_expansion": False,
        "max_transitive_depth": 2,
        "deterministic": True,
    }


def _detect_cycle(start: str) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        spec = get_skill_definition(node)
        if spec is None:
            return False
        for dep in spec["dependency_skills"]:
            if dfs(dep):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return dfs(start)


def validate_dependency_closure(skill_name: str) -> None:
    if get_skill_definition(skill_name) is None:
        raise ValueError("invalid skill")
    if _detect_cycle(skill_name):
        raise ValueError("circular dependency detected")


def validate_skill_inheritance(parent_skill: str, child_skill: str) -> None:
    """
    Reject unsafe inheritance patterns (foundation hook).
    """
    if parent_skill.strip() in {"*", "__unrestricted__", "__all_tools__"}:
        raise ValueError("unsafe skill inheritance rejected")
    if get_skill_definition(parent_skill) is None or get_skill_definition(child_skill) is None:
        raise ValueError("invalid skill for inheritance")
