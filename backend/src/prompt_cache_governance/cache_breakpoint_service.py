"""
MODULE: cache_breakpoint_service
PURPOSE: Cache breakpoint boundary metadata + invalidation reasons (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.prompt_cache_governance.model_session_stability_service import export_model_session_stability
from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry
from src.prompt_cache_governance.tool_schema_stability_service import export_tool_schema_stability

BREAKPOINT_EPOCH = "2026-01-01T00:00:00Z"


def _static_prefix_hash(prefix_components: list[dict[str, Any]]) -> str:
    blob = json.dumps(prefix_components, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def export_cache_breakpoints(*, session_id: str = "sess-demo-001") -> dict[str, Any]:
    sid = (session_id or "").strip() or "sess-demo-001"
    prefix = export_static_prefix_registry()["static_prefix_components"]
    prefix_hash = _static_prefix_hash(prefix)
    tool = export_tool_schema_stability(session_id=sid)
    model = export_model_session_stability(session_id=sid)

    invalidation_reason = None
    cache_valid = True
    if tool["cache_reset_warning"]:
        cache_valid = False
        invalidation_reason = "tool_schema_changed"
    elif any(model["checks"].values()):
        cache_valid = False
        invalidation_reason = "model_changed"

    bp = {
        "breakpoint_id": f"bp:{sid}:001",
        "session_id": sid,
        "static_prefix_hash": prefix_hash,
        "dynamic_suffix_start_index": 0,
        "cache_valid": bool(cache_valid),
        "invalidation_reason": invalidation_reason or "unknown" if not cache_valid else None,
        "created_at": BREAKPOINT_EPOCH,
        "deterministic": True,
        "explainable": True,
        "no_hidden_invalidation": True,
    }
    return {"breakpoints": [bp], "deterministic": True}

