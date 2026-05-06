"""
MODULE: dynamic_index_grouping_service
PURPOSE: Dynamic retrieval grouping identifiers — deterministic metadata (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_dynamic_index_grouping_manifest() -> dict[str, Any]:
    return {
        "groups": [
            {"group_key": "gidx-weekly-ingest-alpha", "document_family": "permit_pdf", "rollover_policy": "size_cap"},
            {"group_key": "gidx-vendor-catalog-beta", "document_family": "csv_row", "rollover_policy": "row_cap"},
        ],
        "self_expanding_index": False,
        "deterministic": True,
    }
