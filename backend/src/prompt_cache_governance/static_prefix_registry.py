"""
MODULE: static_prefix_registry
PURPOSE: Stable static prompt prefix components (cacheable) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
from typing import Any

from src.prompt_cache_governance.prompt_cache_validation_service import detect_volatile_content, require_no_volatile_static_prefix

PREFIX_EPOCH = "2026-01-01T00:00:00Z"

STATIC_COMPONENT_TYPES = (
    "system_rules",
    "tool_definitions",
    "schema_definitions",
    "project_context",
    "guardrails",
    "behavior_guidelines",
)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def export_static_prefix_registry() -> dict[str, Any]:
    # Deterministic minimal content; no timestamps/uuids/random content inside cacheable components.
    components = []
    for ct in STATIC_COMPONENT_TYPES:
        content = f"{ct}:finderos_governed_foundation_v1"
        vol = detect_volatile_content(content)
        components.append(
            {
                "prefix_id": f"prefix:{ct}",
                "prefix_name": f"Static prefix: {ct}",
                "component_type": ct,
                "content_hash": _hash(content),
                "stability_required": True,
                "cacheable": True,
                "volatile_content_detected": bool(vol),
                "created_at": PREFIX_EPOCH,
                "deterministic": True,
            }
        )
    require_no_volatile_static_prefix(components)
    return {"static_prefix_components": components, "deterministic": True, "static_prefix_stable": True}

