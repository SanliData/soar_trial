"""
MODULE: compression_validation_service
PURPOSE: Validate compression outputs and reject unsafe removal semantics (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_compression_manifest(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("invalid compression manifest")
    if manifest.get("llm_invoked") is True:
        raise ValueError("LLM compression forbidden in foundation")
    if manifest.get("deterministic") is not True:
        raise ValueError("compression must be deterministic")


def validate_duplicate_detection(dedup: dict[str, Any]) -> None:
    if not isinstance(dedup, dict):
        raise ValueError("invalid dedupe payload")
    if dedup.get("automatic_deletion") is True:
        raise ValueError("automatic deletion forbidden")
    for k in ("duplicate_groups", "estimated_token_waste", "recommended_removals"):
        if k not in dedup:
            raise ValueError("invalid dedupe payload")

