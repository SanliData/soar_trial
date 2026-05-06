"""
MODULE: graph_cache_service
PURPOSE: Graph intelligence cache metadata — no autonomous writes (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_graph_cache_manifest() -> dict[str, Any]:
    return {
        "cache_entries_template": [
            {
                "key_pattern": "trav:{projection_id}:{start_id}:{depth}",
                "ttl_seconds": 600,
                "stale_invalidates_on_mutation_hook": True,
                "autonomous_invalidation": False,
            }
        ],
        "metadata_only": True,
        "deterministic": True,
    }
