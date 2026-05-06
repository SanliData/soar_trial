"""
ROUTER: context_isolation_router
PURPOSE: HTTP facade for workflow/subagent context isolation (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.context_isolation.context_boundary_service import validate_context_boundary_access
from src.context_isolation.subagent_context_service import build_isolated_subagent_context
from src.context_isolation.workflow_context_partitioning import export_workflow_partitions
from src.context_orchestration.instruction_context_service import export_instruction_context_examples

router = APIRouter(tags=["context-isolation"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "context_isolation_foundation": True,
        "unrestricted_shared_memory": False,
        "hidden_cross_workflow_access": False,
        "autonomous_subagent_mesh": False,
    }
    merged.update(payload)
    return merged


@router.get("/system/context/isolation")
async def get_context_isolation() -> Dict[str, Any]:
    items = export_instruction_context_examples()
    return _envelope(
        {
            "workflows": export_workflow_partitions(),
            "isolated_subagent_sample": build_isolated_subagent_context(
                workflow_scope="procurement_analysis",
                subagent_id="subagent-demo-001",
                context_items=items,
                compression_allowed=True,
            ),
        }
    )


@router.get("/system/context/boundaries")
async def get_context_boundaries() -> Dict[str, Any]:
    item = export_instruction_context_examples()[0]
    within = validate_context_boundary_access(
        requesting_workflow_scope="executive_reporting",
        requested_item={**item, "workflow_scope": "executive_reporting"},
        explicit_cross_workflow_allow=False,
    )
    cross_blocked = validate_context_boundary_access(
        requesting_workflow_scope="executive_reporting",
        requested_item=item,
        explicit_cross_workflow_allow=False,
    )
    cross_allowed = validate_context_boundary_access(
        requesting_workflow_scope="executive_reporting",
        requested_item=item,
        explicit_cross_workflow_allow=True,
    )
    return _envelope({"within_workflow": within, "cross_workflow_blocked": cross_blocked, "cross_workflow_allowed": cross_allowed})


@router.get("/system/context/partitions")
async def get_context_partitions() -> Dict[str, Any]:
    return _envelope({"partitions": export_workflow_partitions()})

