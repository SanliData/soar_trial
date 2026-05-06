"""
MODULE: firewall_validation_service
PURPOSE: Validate firewall metadata — reject unsafe execution policies (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_unsafe_firewall_flags(flags: dict[str, Any] | None) -> None:
    if not flags:
        return
    if flags.get("unrestricted_autonomous_execution") is True:
        raise ValueError("unsafe firewall flag rejected")
    if flags.get("hidden_runtime_override") is True:
        raise ValueError("unsafe firewall flag rejected")
    if flags.get("dynamic_self_modifying_policies") is True:
        raise ValueError("unsafe firewall flag rejected")
    if flags.get("direct_agent_provider_trust") is True:
        raise ValueError("unsafe firewall flag rejected")


def validate_interception_metadata(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("context_only_enforcement") is True and meta.get("proxy_bypass") is True:
        raise ValueError("invalid interception metadata")
