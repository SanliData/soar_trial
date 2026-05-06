"""
ROUTER: agent_harness_router
PURPOSE: HTTP facade for harness registries and compression (H-031)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.agent_harness.compression_service import compress_bundle
from src.agent_harness.harness_runtime_service import (
    generate_runtime_summary,
    get_protocols,
    get_runtime_memory,
    get_active_skills,
)
from src.agent_harness.harness_validation_service import HarnessCompressRequest, validate_memory_type

router = APIRouter(prefix="/system/harness", tags=["agent-harness"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "agent_harness_foundation": True,
        "recursive_agent_swarm": False,
        "unrestricted_subagent_spawning": False,
    }
    out.update(payload)
    return out


@router.get("/memory")
async def get_memory() -> Dict[str, Any]:
    return _envelope(get_runtime_memory())


@router.get("/skills")
async def get_skills() -> Dict[str, Any]:
    return _envelope(get_active_skills())


@router.get("/protocols")
async def get_protocols_route() -> Dict[str, Any]:
    return _envelope(get_protocols())


@router.post("/compress")
async def post_compress(body: HarnessCompressRequest) -> Dict[str, Any]:
    try:
        extra: dict[str, Any] = {}
        if body.mode == "memory":
            mt = body.memory_type or "working_memory"
            validate_memory_type(mt)
            extra["memory_type"] = mt
        if body.mode == "trajectory" and body.trajectory_steps:
            extra["steps"] = body.trajectory_steps
        result = compress_bundle(body.mode, body.payload, extra)
        return _envelope({"compression": result})
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/runtime-summary")
async def get_runtime_summary() -> Dict[str, Any]:
    return _envelope({"summary": generate_runtime_summary()})
