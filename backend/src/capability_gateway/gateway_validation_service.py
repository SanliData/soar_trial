"""
MODULE: gateway_validation_service
PURPOSE: Validate gateway definitions and reject unsafe execution flags (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.capability_gateway.mcp_gateway_registry import GATEWAYS


def validate_gateway_name(name: str) -> None:
    key = name.strip()
    if key not in GATEWAYS:
        raise ValueError("invalid gateway name")


def validate_execution_scope(scope: str) -> None:
    allowed = frozenset(
        {
            "sandboxed_dom",
            "read_only_http",
            "bounded_api",
            "ephemeral_parse",
            "internal",
        }
    )
    s = scope.strip()
    if s not in allowed:
        raise ValueError("invalid execution scope")


def validate_unsafe_execution_flags(flags: dict[str, Any] | None) -> None:
    if not flags:
        return
    if flags.get("unrestricted_external_execution") is True:
        raise ValueError("unsafe execution flag rejected")
    if flags.get("autonomous_internet_orchestration") is True:
        raise ValueError("unsafe execution flag rejected")
    if flags.get("unrestricted_tool_chaining") is True:
        raise ValueError("unsafe execution flag rejected")
    if flags.get("unrestricted_browser_automation") is True:
        raise ValueError("unsafe execution flag rejected")
