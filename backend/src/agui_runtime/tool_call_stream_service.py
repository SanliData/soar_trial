"""
MODULE: tool_call_stream_service
PURPOSE: Tool-call stream metadata (capability lineage preserved) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.semantic_capabilities.capability_loader import load_capabilities


def export_tool_streams() -> dict[str, Any]:
    caps = load_capabilities()
    sample = []
    for cid in sorted(list(caps.keys()))[:3]:
        c = caps[cid]
        sample.append(
            {
                "tool_name": cid,
                "capability_scope": c.get("domain"),
                "execution_status": "metadata_only",
                "approval_required": bool(c.get("human_approval_required")),
                "runtime_cost_estimate": {"token_cost": 120, "deterministic": True},
                "capability_lineage": {"capability_id": cid, "endpoint": c.get("endpoint"), "deterministic": True},
                "deterministic": True,
            }
        )
    return {"tool_streams": sample, "deterministic": True, "metadata_only": True}

