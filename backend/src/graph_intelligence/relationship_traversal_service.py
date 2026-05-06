"""
MODULE: relationship_traversal_service
PURPOSE: Multi-hop traversal metadata — bounded depth (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_MAX_DEPTH = 4


def plan_relationship_traversal(
    *,
    start_kind: str,
    relationship_goal: str,
    requested_depth: int,
) -> dict[str, Any]:
    depth = min(max(requested_depth, 1), _MAX_DEPTH)
    examples_domain = ""
    if "contractor" in relationship_goal.lower():
        examples_domain = "contractor_relationships"
    elif "utility" in relationship_goal.lower():
        examples_domain = "utility_relationships"
    elif "subcontractor" in relationship_goal.lower():
        examples_domain = "subcontractor_chains"
    elif "lineage" in relationship_goal.lower() or "project" in relationship_goal.lower():
        examples_domain = "project_lineage"
    return {
        "start_kind": start_kind,
        "relationship_goal": relationship_goal,
        "effective_depth": depth,
        "max_depth_allowed": _MAX_DEPTH,
        "examples_domain": examples_domain or "generic_operational",
        "hybrid_query_compatible": True,
        "explainable_hops": [f"hop_{i}" for i in range(1, depth + 1)],
        "deterministic": True,
    }


def export_relationship_traversal_manifest() -> dict[str, Any]:
    return {
        "sample_plans": [
            plan_relationship_traversal(
                start_kind="contractor", relationship_goal="contractor_to_utility", requested_depth=3
            ),
            plan_relationship_traversal(
                start_kind="project", relationship_goal="project_lineage", requested_depth=_MAX_DEPTH
            ),
        ],
        "deterministic": True,
    }
