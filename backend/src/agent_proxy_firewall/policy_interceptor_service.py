"""
MODULE: policy_interceptor_service
PURPOSE: Infrastructure-level AI policy interception metadata (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_POLICY_DOMAINS: dict[str, dict[str, Any]] = {
    "procurement_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "onboarding_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "browser_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "graph_mutation_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "external_execution_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "export_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    ***REMOVED*** H-044 recognizers (detection + interception only; no execution)
    "guardrail_context_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "tool_context_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "mcp_projection_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "document_derived_content_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    ***REMOVED*** H-045 recognizers (detection + interception only; no autonomous enforcement)
    "nl_command_risk_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "agent_dispatch_risk_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "connector_execution_risk_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "retrieval_expansion_risk_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    ***REMOVED*** H-048 recognizers (detection + interception only; no execution)
    "generated_ui_action_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "tool_event_stream_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "approval_bypass_attempt_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "unsafe_event_propagation_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    ***REMOVED*** H-049 recognizers (detection + governance only)
    "identity_scope_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "shadow_agent_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "unauthorized_mcp_endpoint_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "suspicious_capability_escalation_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "runtime_attribution_gap_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    ***REMOVED*** H-050 recognizers (detection + governance only; no autonomous deployment)
    "unsafe_public_deployment_profile_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "cache_breaking_tool_schema_mutation_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "model_switch_during_governed_session_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "volatile_static_prefix_content_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
    "unrestricted_external_channel_activation_policy": {"enforcement_surface": "proxy_gateway", "context_only_allowed": False},
}


def export_policy_interception_manifest() -> dict[str, Any]:
    return {
        "policy_domains": dict(_POLICY_DOMAINS),
        "proxy_level_enforcement": True,
        "dynamic_self_modifying_policies": False,
    }


def validate_policy_domain(domain: str) -> None:
    if domain.strip() not in _POLICY_DOMAINS:
        raise ValueError("invalid policy domain")
