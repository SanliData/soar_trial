"""
MODULE: context_boundary_service
PURPOSE: Validate explicit cross-context boundary access (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.context_isolation.workflow_context_partitioning import get_partition
from src.context_orchestration.context_validation_service import validate_context_item


def validate_context_boundary_access(
    *,
    requesting_workflow_scope: str,
    requested_item: dict[str, Any],
    explicit_cross_workflow_allow: bool = False,
) -> dict[str, Any]:
    """
    Rules:
    - by default, contexts are workflow-scoped
    - cross-workflow access must be explicit and auditable
    """
    wf = (requesting_workflow_scope or "").strip()
    if not wf:
        raise ValueError("invalid workflow_scope")

    validate_context_item(requested_item)
    item_wf = str(requested_item.get("workflow_scope") or "").strip()
    if not item_wf:
        raise ValueError("invalid requested context workflow_scope")

    partition = get_partition(wf)
    allowed_types = set(partition["allowed_context_types"])
    ct = str(requested_item["context_type"]).strip()
    if ct not in allowed_types:
        raise ValueError("context_type not allowed for workflow")

    cross = wf != item_wf
    if cross and not explicit_cross_workflow_allow:
        return {
            "allowed": False,
            "reason": "cross_workflow_access_requires_explicit_allow",
            "requesting_workflow_scope": wf,
            "requested_workflow_scope": item_wf,
            "deterministic": True,
        }

    return {
        "allowed": True,
        "reason": "within_workflow" if not cross else "explicit_cross_workflow_allow",
        "requesting_workflow_scope": wf,
        "requested_workflow_scope": item_wf,
        "deterministic": True,
    }

