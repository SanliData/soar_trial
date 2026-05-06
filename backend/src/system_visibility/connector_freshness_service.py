"""
MODULE: connector_freshness_service
PURPOSE: Connector freshness classification (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.connector_registry_service import export_connector_registry
from src.federated_retrieval.incremental_sync_service import export_incremental_sync_status


def _classify_connector(*, enabled: bool, freshness_status: str, freshness_days: int) -> str:
    if not enabled:
        return "disconnected"
    if freshness_status == "disabled":
        return "disconnected"
    if freshness_days <= 7:
        return "healthy"
    if freshness_days <= 30:
        return "stale"
    if freshness_days <= 90:
        return "degraded"
    return "disconnected"


def export_connector_freshness() -> dict[str, Any]:
    reg = export_connector_registry()["connectors"]
    sync = {r["connector_name"]: r for r in export_incremental_sync_status()["sync"]}
    rows = []
    for c in reg:
        s = sync.get(c["connector_name"], {})
        enabled = bool(c["enabled"])
        freshness_days = 7 if enabled else 999
        last_sync = s.get("last_sync_at")
        freshness_status = str(s.get("freshness_status") or ("ok" if enabled else "disabled"))
        status = _classify_connector(enabled=enabled, freshness_status=freshness_status, freshness_days=freshness_days)
        reliability = 0.85 if status == "healthy" else 0.65 if status == "stale" else 0.45 if status == "degraded" else 0.2
        rows.append(
            {
                "connector_name": c["connector_name"],
                "status": status,
                "last_sync": last_sync,
                "freshness_days": freshness_days,
                "estimated_sync_gap": "foundation_metadata_only",
                "retrieval_reliability_score": round(reliability, 4),
                "deterministic": True,
            }
        )
    rows.sort(key=lambda r: r["connector_name"])
    return {"connectors": rows, "deterministic": True}

