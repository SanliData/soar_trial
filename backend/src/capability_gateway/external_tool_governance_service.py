"""
MODULE: external_tool_governance_service
PURPOSE: Auditable external tool governance — bounded chaining (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_TOOL_REGISTRY: list[dict[str, Any]] = [
    {
        "tool_id": "http_read_v1",
        "trust_level": "medium",
        "domain_allowlist_required": True,
        "replay_logging": True,
        "escalation_on_denied_domain": True,
        "max_chain_depth": 1,
    },
    {
        "tool_id": "structured_parse_v1",
        "trust_level": "high",
        "domain_allowlist_required": False,
        "replay_logging": True,
        "escalation_on_denied_domain": False,
        "max_chain_depth": 1,
    },
]


def export_external_tool_governance() -> dict[str, Any]:
    return {
        "tools": list(_TOOL_REGISTRY),
        "unrestricted_tool_chaining": False,
        "audit_required": True,
        "deterministic_registry": True,
    }
