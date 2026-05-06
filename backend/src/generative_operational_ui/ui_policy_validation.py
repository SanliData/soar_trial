"""
MODULE: ui_policy_validation
PURPOSE: Validate governed UI payloads (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def reject_executable_payload(component: dict[str, Any]) -> None:
    if component.get("raw_html"):
        raise ValueError("raw_html rejected")
    if component.get("raw_js"):
        raise ValueError("raw_js rejected")
    if component.get("executable_payload") is True:
        raise ValueError("executable payload rejected")


def enforce_registry_component_type(component_type: str, allowed: set[str]) -> None:
    if (component_type or "").strip() not in allowed:
        raise ValueError("unapproved component type")

