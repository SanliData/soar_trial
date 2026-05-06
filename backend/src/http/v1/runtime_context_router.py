"""
ROUTER: runtime_context_router
PURPOSE: HTTP facade for runtime metadata and context budgeting (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Query

from src.runtime_context.backend_metadata_service import build_backend_metadata_snapshot
from src.runtime_context.capability_snapshot_service import build_capability_snapshots
from src.runtime_context.context_budget_service import apply_context_budget
from src.runtime_context.context_trace_service import get_context_trace_store
from src.runtime_context.orchestration_context_service import build_runtime_bundle
from src.runtime_context.runtime_context_validation_service import ContextBudgetRequest
from src.runtime_context.runtime_hint_service import build_runtime_hints
from src.runtime_context.runtime_topology_service import build_topology_snapshot

router = APIRouter(prefix="/system/runtime", tags=["runtime-context"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "runtime_context_foundation": True,
        "autonomous_orchestration_mesh": False,
        "runtime_self_modification": False,
    }
    out.update(payload)
    return out


@router.get("/metadata")
async def get_metadata() -> Dict[str, Any]:
    return _envelope({"snapshot": build_backend_metadata_snapshot()})


@router.get("/capabilities")
async def get_capabilities(
    depth: str = Query(default="summary", description="summary or full"),
) -> Dict[str, Any]:
    try:
        return _envelope(build_capability_snapshots(depth))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/topology")
async def get_topology() -> Dict[str, Any]:
    return _envelope({"topology": build_topology_snapshot()})


@router.get("/hints")
async def get_hints() -> Dict[str, Any]:
    bundle = build_runtime_bundle()
    hints = build_runtime_hints(bundle)
    return _envelope({"hints": hints, "orchestration": bundle.get("orchestration_context")})


@router.post("/context-budget")
async def post_context_budget(body: ContextBudgetRequest) -> Dict[str, Any]:
    result = apply_context_budget(body.estimated_chars, body.requested_layers, body.large_text_sample)
    trace = get_context_trace_store().append(
        "context_budget_applied",
        {"estimated_chars": body.estimated_chars, "layers": list(body.requested_layers)},
    )
    return _envelope({"budget": result, "trace": trace})
