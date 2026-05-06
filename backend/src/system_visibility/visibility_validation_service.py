"""
MODULE: visibility_validation_service
PURPOSE: Validate visibility payloads and reject unsafe override semantics (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_no_hidden_status_overrides(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("hidden_status_override") is True:
        raise ValueError("hidden status override rejected")
    if meta.get("fake_uptime_metrics") is True:
        raise ValueError("fake uptime metrics rejected")


def validate_pressure_level(level: str) -> None:
    if (level or "").strip() not in {"healthy", "elevated", "high", "critical"}:
        raise ValueError("invalid pressure level")

