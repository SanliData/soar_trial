"""
MODULE: long_context_validation_service
PURPOSE: Reject uncontrolled long-context and exposure intents (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_long_context_intent(intent: dict[str, Any] | None) -> None:
    if not intent:
        return
    if intent.get("unrestricted_long_context_workflows") is True:
        raise ValueError("unrestricted long-context rejected")
    if intent.get("load_full_corpus_default") is True:
        raise ValueError("full-context default loading rejected")


def validate_sparse_metadata_row(row: dict[str, Any]) -> None:
    if "provider_name" not in row:
        raise ValueError("invalid sparse metadata row")
    if row.get("hidden_moe_weights") is True:
        raise ValueError("hidden ensemble routing rejected")
