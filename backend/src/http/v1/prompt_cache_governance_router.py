"""
ROUTER: prompt_cache_governance_router
PURPOSE: Prompt cache governance facade (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.prompt_cache_governance.cache_breakpoint_service import export_cache_breakpoints
from src.prompt_cache_governance.cache_efficiency_service import export_cache_efficiency
from src.prompt_cache_governance.cache_safe_compression_service import export_cache_safe_compression
from src.prompt_cache_governance.dynamic_suffix_service import export_dynamic_suffix
from src.prompt_cache_governance.model_session_stability_service import export_model_session_stability
from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry
from src.prompt_cache_governance.tool_schema_stability_service import export_tool_schema_stability

router = APIRouter(prefix="/system/cache", tags=["prompt-cache-governance"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "prompt_cache_governance_foundation": True,
        "static_prefix_disciplined": True,
        "no_hidden_prefix_mutation": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/static-prefix")
async def get_static_prefix() -> Dict[str, Any]:
    return _envelope(export_static_prefix_registry())


@router.get("/dynamic-suffix")
async def get_dynamic_suffix() -> Dict[str, Any]:
    return _envelope(export_dynamic_suffix(session_id="sess-demo-001"))


@router.get("/breakpoints")
async def get_breakpoints() -> Dict[str, Any]:
    return _envelope(export_cache_breakpoints(session_id="sess-demo-001"))


@router.get("/efficiency")
async def get_efficiency() -> Dict[str, Any]:
    return _envelope(export_cache_efficiency())


@router.get("/tool-schema-stability")
async def get_tool_schema_stability() -> Dict[str, Any]:
    return _envelope(export_tool_schema_stability(session_id="sess-demo-001"))


@router.get("/model-session-stability")
async def get_model_session_stability() -> Dict[str, Any]:
    return _envelope(export_model_session_stability(session_id="sess-demo-001"))


@router.get("/compression")
async def get_compression() -> Dict[str, Any]:
    return _envelope(export_cache_safe_compression(session_id="sess-demo-001"))

