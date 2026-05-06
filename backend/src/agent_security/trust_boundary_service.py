"""
MODULE: trust_boundary_service
PURPOSE: Fail-closed capability boundary checks (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from urllib.parse import urlparse

from src.agent_security.tool_capability_registry import get_tool_capability


def validate_tool_invocation(
    tool_name: str,
    action: str,
    domain: str | None,
) -> dict[str, str | bool]:
    """
    Explicit allow rules only. Raises ValueError when invocation cannot proceed.
    Returns audit dict on success.
    """
    cap = get_tool_capability(tool_name)
    if cap is None:
        raise ValueError(f"unknown tool: {tool_name}")
    if action not in cap.allowed_actions:
        raise ValueError(f"action '{action}' not allowed for tool '{tool_name}'")
    if domain:
        host = _host_only(domain)
        if cap.allowed_domains and host not in cap.allowed_domains:
            raise ValueError(f"domain '{host}' not in allow-list for '{tool_name}'")
    return {
        "tool_name": tool_name,
        "action": action,
        "trust_level": cap.trust_level,
        "external_execution": cap.external_execution,
        "requires_human_approval": cap.requires_human_approval,
        "passed": True,
    }


def assert_escalation_blocked(current_trust: str, requested_trust: str) -> None:
    """Prevent implicit trust-tier escalation across tool hops."""
    order = ("sandbox_only", "external_unverified", "trusted_partner", "verified_internal")
    try:
        cu = order.index(current_trust)
        rq = order.index(requested_trust)
    except ValueError as exc:
        raise ValueError("invalid trust level for escalation check") from exc
    if rq > cu:
        raise ValueError("trust escalation blocked — explicit governance approval required")


def _host_only(domain_or_url: str) -> str:
    d = domain_or_url.strip()
    if "://" in d:
        p = urlparse(d)
        return (p.hostname or "").lower()
    return d.lower()
