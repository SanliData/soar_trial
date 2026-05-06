"""
MODULE: capability_snapshot_service
PURPOSE: Summary-first capability rows for progressive loading (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.semantic_capabilities.capability_loader import load_capabilities


def build_capability_snapshots(depth: str = "summary") -> dict[str, Any]:
    if depth not in ("summary", "full"):
        raise ValueError("depth must be summary or full")
    caps = load_capabilities()
    rows: list[dict[str, Any]] = []
    for c in caps:
        row: dict[str, Any] = {
            "capability_name": c.capability_id,
            "capability_type": c.domain,
            "orchestration_safe": c.orchestration_safe,
            "requires_human_approval": c.human_approval_required,
            "trust_level": "restricted" if c.risk_level == "high" else "standard",
            "status": "active",
            "metadata_summary": c.description[:160] + ("…" if len(c.description) > 160 else ""),
        }
        if depth == "full":
            row["endpoint"] = c.endpoint
            row["http_method"] = c.http_method
        rows.append(row)
    return {
        "depth": depth,
        "count": len(rows),
        "capabilities": rows,
        "progressive_loading": True,
    }
