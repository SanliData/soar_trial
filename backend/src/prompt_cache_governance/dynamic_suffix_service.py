"""
MODULE: dynamic_suffix_service
PURPOSE: Dynamic suffix components (auditable; never mutates static prefix) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

SUFFIX_EPOCH = "2026-01-01T00:00:00Z"


def export_dynamic_suffix(*, session_id: str = "sess-demo-001") -> dict[str, Any]:
    sid = (session_id or "").strip() or "sess-demo-001"
    components = [
        {"type": "user_messages", "count": 2, "auditable": True, "deterministic": True},
        {"type": "assistant_turns", "count": 2, "auditable": True, "deterministic": True},
        {"type": "tool_outputs", "count": 1, "auditable": True, "deterministic": True},
        {"type": "runtime_observations", "count": 1, "auditable": True, "deterministic": True},
        {"type": "event_stream_updates", "count": 1, "auditable": True, "deterministic": True},
        {"type": "approval_events", "count": 0, "auditable": True, "deterministic": True},
    ]
    return {
        "session_id": sid,
        "dynamic_suffix_components": components,
        "static_prefix_mutated": False,
        "created_at": SUFFIX_EPOCH,
        "deterministic": True,
        "auditable": True,
    }

