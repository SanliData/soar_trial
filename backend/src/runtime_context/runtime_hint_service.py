"""
MODULE: runtime_hint_service
PURPOSE: Concise deterministic hints for orchestrators (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def build_runtime_hints(bundle: dict[str, Any]) -> list[str]:
    """
    Token-efficient bullet hints derived only from structured bundle fields.
    """
    hints: list[str] = []
    meta = bundle.get("backend_metadata") or {}
    orch = bundle.get("orchestration_context") or {}

    if meta.get("graph_status") == "available":
        hints.append("use graph traversal for relationship-heavy workflows")
    if meta.get("ingestion_status") == "degraded":
        hints.append("avoid expensive retrieval path — ingestion freshness degraded")
    else:
        hints.append("prefer cached summaries when repeating capability lookups")

    if orch.get("security_escalation_required"):
        hints.append("security escalation required — gate tool calls")

    if meta.get("widget_status") == "enabled":
        hints.append("widget rendering available — prefer structured JSON widget envelopes")

    hints.append("use structured JSON outputs for orchestration stability")

    # Dedupe preserving order
    seen: set[str] = set()
    out: list[str] = []
    for h in hints:
        if h not in seen:
            seen.add(h)
            out.append(h)
    return out[:12]
