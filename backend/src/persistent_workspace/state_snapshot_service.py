"""
MODULE: state_snapshot_service
PURPOSE: Snapshot metadata for audit and resume — immutable preference (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_state_snapshot_manifest() -> dict[str, Any]:
    return {
        "snapshots": [
            {
                "snapshot_id": "ss-tenant-alpha-001",
                "includes_state_types": ["workflow_state", "evaluation_state"],
                "immutable_preferred": True,
                "checksum_algorithm": "sha256",
            }
        ],
        "deterministic": True,
    }
