"""
MODULE: compressed_embedding_service
PURPOSE: Compressed embedding metadata (no vector DB rewrite) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_compressed_embedding_manifest() -> dict[str, Any]:
    return {
        "embedding_mode": "metadata_only",
        "vector_db_required": False,
        "model_dependency_required_now": False,
        "compression_strategy": "store_chunk_hash_and_summary_only",
        "deterministic": True,
    }

