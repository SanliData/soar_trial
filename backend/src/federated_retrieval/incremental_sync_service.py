"""
MODULE: incremental_sync_service
PURPOSE: Incremental sync policy/status (metadata only) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.connector_registry_service import export_connector_registry


def export_incremental_sync_status() -> dict[str, Any]:
    conns = export_connector_registry()["connectors"]
    rows = []
    stale = 0
    warnings = 0
    ***REMOVED*** Deterministic foundation timestamp (no live sync executed).
    now = "2026-01-01T00:00:00Z"
    for c in conns:
        enabled = bool(c["enabled"])
        freshness_status = "ok" if enabled else "disabled"
        changed = 0 if not enabled else 12
        sync_warnings = []
        if not enabled:
            sync_warnings.append("connector_disabled")
            warnings += 1
        if c["sync_mode"].endswith("_deferred") and enabled:
            sync_warnings.append("sync_deferred_foundation_only")
        row = {
            "connector_name": c["connector_name"],
            "last_sync_at": now if enabled else None,
            "sync_mode": c["sync_mode"],
            "changed_items_estimate": changed,
            "freshness_status": freshness_status,
            "sync_warnings": sync_warnings,
        }
        if freshness_status != "ok":
            stale += 1
        rows.append(row)
    return {
        "sync": rows,
        "stale_connector_count": stale,
        "warning_count": warnings,
        "metadata_only": True,
        "no_live_external_sync": True,
        "deterministic": True,
    }

