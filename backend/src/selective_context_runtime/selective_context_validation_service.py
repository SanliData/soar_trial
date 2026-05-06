"""
MODULE: selective_context_validation_service
PURPOSE: Validate selective context metadata and reject uncontrolled expansion (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_no_uncontrolled_retrieval_expansion(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unlimited_retrieval_expansion") is True:
        raise ValueError("unlimited retrieval expansion rejected")
    if meta.get("hidden_context_expansion") is True:
        raise ValueError("hidden context expansion rejected")
    if meta.get("rl_training_enabled") is True:
        raise ValueError("RL training infrastructure rejected")


def validate_chunk_record(chunk: dict[str, Any]) -> None:
    if not isinstance(chunk, dict):
        raise ValueError("invalid chunk record")
    required = {"chunk_id", "original_token_estimate", "compressed_token_estimate", "compression_ratio", "source_lineage", "expansion_allowed"}
    if required - chunk.keys():
        raise ValueError("chunk record missing fields")
    if not isinstance(chunk.get("source_lineage"), dict) or not chunk["source_lineage"]:
        raise ValueError("chunk lineage required")

