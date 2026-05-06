"""
MODULE: connector_registry_service
PURPOSE: Federated connector registry (metadata only) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.federated_retrieval.federated_retrieval_validation_service import validate_connector_record

CONNECTOR_EPOCH = "2026-01-01T00:00:00Z"

CONNECTORS: dict[str, dict[str, Any]] = {
    "uploaded_documents": {
        "connector_name": "uploaded_documents",
        "connector_type": "internal_repository",
        "auth_mode": "internal",
        "sync_mode": "manual_upload",
        "source_authority": 0.6,
        "freshness_policy": "event_time_based",
        "enabled": True,
        "created_at": CONNECTOR_EPOCH,
    },
    "github": {
        "connector_name": "github",
        "connector_type": "developer_knowledge",
        "auth_mode": "oauth_deferred",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.72,
        "freshness_policy": "commit_time_based",
        "enabled": False,
        "created_at": CONNECTOR_EPOCH,
    },
    "slack": {
        "connector_name": "slack",
        "connector_type": "enterprise_chat",
        "auth_mode": "oauth_deferred",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.55,
        "freshness_policy": "message_time_based",
        "enabled": False,
        "created_at": CONNECTOR_EPOCH,
    },
    "jira": {
        "connector_name": "jira",
        "connector_type": "ticketing",
        "auth_mode": "oauth_deferred",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.65,
        "freshness_policy": "issue_update_time_based",
        "enabled": False,
        "created_at": CONNECTOR_EPOCH,
    },
    "linear": {
        "connector_name": "linear",
        "connector_type": "project_tracking",
        "auth_mode": "oauth_deferred",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.62,
        "freshness_policy": "issue_update_time_based",
        "enabled": False,
        "created_at": CONNECTOR_EPOCH,
    },
    "notion": {
        "connector_name": "notion",
        "connector_type": "enterprise_docs",
        "auth_mode": "oauth_deferred",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.58,
        "freshness_policy": "page_update_time_based",
        "enabled": False,
        "created_at": CONNECTOR_EPOCH,
    },
    "procurement_feed": {
        "connector_name": "procurement_feed",
        "connector_type": "official_feed",
        "auth_mode": "public_feed",
        "sync_mode": "scheduled_deferred",
        "source_authority": 0.88,
        "freshness_policy": "feed_time_based",
        "enabled": True,
        "created_at": CONNECTOR_EPOCH,
    },
    "permit_repository": {
        "connector_name": "permit_repository",
        "connector_type": "public_registry",
        "auth_mode": "public_registry",
        "sync_mode": "incremental_deferred",
        "source_authority": 0.78,
        "freshness_policy": "record_update_time_based",
        "enabled": True,
        "created_at": CONNECTOR_EPOCH,
    },
    "contractor_documents": {
        "connector_name": "contractor_documents",
        "connector_type": "internal_repository",
        "auth_mode": "internal",
        "sync_mode": "manual_upload",
        "source_authority": 0.66,
        "freshness_policy": "event_time_based",
        "enabled": True,
        "created_at": CONNECTOR_EPOCH,
    },
}


def export_connector_registry() -> dict[str, Any]:
    rows = []
    for k in sorted(CONNECTORS.keys()):
        row = dict(CONNECTORS[k])
        validate_connector_record(row)
        rows.append(row)
    return {
        "connectors": rows,
        "connector_count": len(rows),
        "metadata_only": True,
        "no_live_external_sync": True,
        "deterministic": True,
    }


def get_connector(connector_name: str) -> dict[str, Any]:
    key = (connector_name or "").strip()
    if key not in CONNECTORS:
        raise ValueError("unknown connector")
    row = dict(CONNECTORS[key])
    validate_connector_record(row)
    return row

