"""
MODULE: federated_retrieval_validation_service
PURPOSE: Validate federated retrieval metadata; reject uncontrolled execution (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_connector_record(conn: dict[str, Any]) -> None:
    if not isinstance(conn, dict):
        raise ValueError("invalid connector record")
    required = {
        "connector_name",
        "connector_type",
        "auth_mode",
        "sync_mode",
        "source_authority",
        "freshness_policy",
        "enabled",
        "created_at",
    }
    if required - conn.keys():
        raise ValueError("connector missing required fields")
    if not isinstance(conn.get("enabled"), bool):
        raise ValueError("invalid enabled")
    if conn.get("contains_secrets") is True:
        raise ValueError("secrets forbidden in connector metadata")
    if conn.get("live_external_sync_enabled") is True:
        raise ValueError("live external sync forbidden in foundation")


def validate_retrieval_result(row: dict[str, Any]) -> None:
    if not isinstance(row, dict):
        raise ValueError("invalid retrieval result")
    if "source_lineage" not in row:
        raise ValueError("lineage required for retrieval result")
    lineage = row.get("source_lineage")
    if not isinstance(lineage, dict) or not lineage:
        raise ValueError("invalid lineage")

