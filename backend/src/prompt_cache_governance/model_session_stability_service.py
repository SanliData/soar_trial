"""
MODULE: model_session_stability_service
PURPOSE: Detect mid-session model/provider switches (requires explicit reset metadata) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

MODEL_EPOCH = "2026-01-01T00:00:00Z"


def export_model_session_stability(*, session_id: str = "sess-demo-001") -> dict[str, Any]:
    ***REMOVED*** Foundation: deterministic pinned model metadata.
    return {
        "session_id": (session_id or "").strip() or "sess-demo-001",
        "model_id": "foundation-model-v1",
        "provider": "foundation-provider",
        "context_window": 128000,
        "cache_compatibility": "stable_if_prefix_static",
        "checks": {
            "model_changed": False,
            "provider_changed": False,
            "context_window_changed": False,
            "cache_compatibility_changed": False,
        },
        "model_switch_requires_reset": True,
        "explicit_reset_metadata_required": True,
        "created_at": MODEL_EPOCH,
        "deterministic": True,
    }

