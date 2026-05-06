"""
MODULE: runtime_access_validation
PURPOSE: Validate unsafe runtime exposure intents (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_runtime_access_intent(intent: dict[str, Any] | None) -> None:
    if not intent:
        return
    if intent.get("expose_ai_runtime_publicly") is True:
        raise ValueError("public ai runtime exposure rejected")
    if intent.get("unrestricted_network_execution_mesh") is True:
        raise ValueError("unrestricted network mesh rejected")
    if intent.get("uncontrolled_persistent_execution_bridge") is True:
        raise ValueError("uncontrolled persistent execution rejected")
