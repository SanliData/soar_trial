"""
MODULE: cross_context_validation
PURPOSE: Validate isolation invariants and reject hidden cross-workflow sharing (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_no_unrestricted_shared_context(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unrestricted_shared_context") is True:
        raise ValueError("unrestricted shared context rejected")
    if meta.get("hidden_cross_workflow_access") is True:
        raise ValueError("hidden cross-workflow access rejected")
    if meta.get("shared_global_context_blob") is True:
        raise ValueError("global context blob rejected")

