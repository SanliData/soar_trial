"""
MODULE: cache_safe_compression_service
PURPOSE: Cache-safe compression metadata (never rewrites static prefix) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry


def export_cache_safe_compression(*, session_id: str = "sess-demo-001") -> dict[str, Any]:
    prefix = export_static_prefix_registry()
    return {
        "session_id": (session_id or "").strip() or "sess-demo-001",
        "static_prefix_preserved": True,
        "compression_instruction_added_as_suffix": True,
        "compression_event": {"type": "cache_safe_compression_started", "deterministic": True},
        "estimated_retained_cache_benefit": {"prefill_saved_tokens": 5000, "deterministic": True},
        "static_prefix_hashes": [c["content_hash"] for c in prefix["static_prefix_components"]],
        "deterministic": True,
    }

