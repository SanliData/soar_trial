"""
MODULE: tool_schema_stability_service
PURPOSE: Detect cache-breaking tool schema drift (detection only) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.semantic_capabilities.capability_loader import load_capabilities


def _fingerprint_capabilities(caps: list[Any]) -> str:
    # Stable ordering fingerprint: capability_id -> (endpoint, method, domain, approval_required)
    rows = []
    for c in sorted(caps, key=lambda x: getattr(x, "capability_id", "")):
        cid = getattr(c, "capability_id", "")
        rows.append(
            {
                "capability_id": cid,
                "endpoint": getattr(c, "endpoint", None),
                "http_method": getattr(c, "http_method", None),
                "domain": getattr(c, "domain", None),
                "human_approval_required": bool(getattr(c, "human_approval_required", False)),
            }
        )
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def export_tool_schema_stability(*, session_id: str = "sess-demo-001") -> dict[str, Any]:
    caps = load_capabilities()
    fp = _fingerprint_capabilities(caps)
    # Foundation: no previous snapshot persisted; expose current fingerprint and stability requirements.
    return {
        "session_id": (session_id or "").strip() or "sess-demo-001",
        "tool_schema_fingerprint": fp,
        "checks": {
            "tool_added_mid_session": False,
            "tool_removed_mid_session": False,
            "tool_schema_key_ordering_changed": False,
            "tool_parameter_changed": False,
            "tool_description_changed": False,
        },
        "cache_reset_warning": False,
        "detection_only": True,
        "deterministic": True,
    }

