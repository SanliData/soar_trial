"""
MODULE: proxy_gateway_service
PURPOSE: Deterministic AI proxy gateway metadata — interception-only foundation (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

PROXY_GATEWAY_EPOCH = "2025-05-01T00:00:00Z"

PROXY_GATEWAYS: dict[str, dict[str, Any]] = {
    "primary_llm_proxy": {
        "gateway_name": "primary_llm_proxy",
        "interception_enabled": True,
        "input_filters": ["prompt_injection_scan", "scope_allowlist_check", "action_token_scan"],
        "output_filters": ["destructive_command_scan", "browser_action_scan", "workflow_mutation_scan"],
        "policy_domains": [
            "external_execution_policy",
            "export_policy",
            "onboarding_policy",
            "guardrail_context_policy",
            "tool_context_policy",
            "mcp_projection_policy",
            "document_derived_content_policy",
            "nl_command_risk_policy",
            "agent_dispatch_risk_policy",
            "connector_execution_risk_policy",
            "retrieval_expansion_risk_policy",
            "generated_ui_action_policy",
            "tool_event_stream_policy",
            "approval_bypass_attempt_policy",
            "unsafe_event_propagation_policy",
            "identity_scope_policy",
            "shadow_agent_policy",
            "unauthorized_mcp_endpoint_policy",
            "suspicious_capability_escalation_policy",
            "runtime_attribution_gap_policy",
            ***REMOVED*** H-050 cache + deployment governance recognizers
            "unsafe_public_deployment_profile_policy",
            "cache_breaking_tool_schema_mutation_policy",
            "model_switch_during_governed_session_policy",
            "volatile_static_prefix_content_policy",
            "unrestricted_external_channel_activation_policy",
        ],
        "execution_scopes": ["sandboxed_invoke", "read_only_upstream"],
        "audit_required": True,
        "created_at": PROXY_GATEWAY_EPOCH,
    },
    "browser_orchestration_proxy": {
        "gateway_name": "browser_orchestration_proxy",
        "interception_enabled": True,
        "input_filters": ["prompt_injection_scan", "domain_allowlist_precheck"],
        "output_filters": ["browser_action_scan", "destructive_command_scan"],
        "policy_domains": ["browser_policy", "external_execution_policy"],
        "execution_scopes": ["sandbox_browser_only"],
        "audit_required": True,
        "created_at": PROXY_GATEWAY_EPOCH,
    },
}


def export_proxy_gateways_manifest() -> list[dict[str, Any]]:
    return [dict(PROXY_GATEWAYS[k]) for k in sorted(PROXY_GATEWAYS.keys())]


def get_proxy_gateway(name: str) -> dict[str, Any] | None:
    key = name.strip()
    if key not in PROXY_GATEWAYS:
        return None
    return dict(PROXY_GATEWAYS[key])
