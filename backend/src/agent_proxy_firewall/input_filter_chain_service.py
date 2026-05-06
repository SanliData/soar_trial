"""
MODULE: input_filter_chain_service
PURPOSE: Inbound request filter chain metadata and deterministic assessment (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

INPUT_FILTER_CHAIN: list[dict[str, Any]] = [
    {
        "filter_id": "prompt_injection_scan",
        "sequence": 1,
        "checks": ["delimiter_override_strings", "role_confusion_patterns"],
        "violations_action": "block_and_trace",
        "deterministic": True,
    },
    {
        "filter_id": "scope_allowlist_check",
        "sequence": 2,
        "checks": ["workspace_execution_scope_match", "capability_gateway_alignment"],
        "violations_action": "block_and_trace",
        "deterministic": True,
    },
    {
        "filter_id": "action_token_scan",
        "sequence": 3,
        "checks": ["destructive_verbs_without_grant", "shell_invocation_fragments"],
        "violations_action": "block_and_escalate",
        "deterministic": True,
    },
    {
        "filter_id": "domain_allowlist_precheck",
        "sequence": 4,
        "checks": ["http_target_domain_allowlist_stub"],
        "violations_action": "block_and_trace",
        "deterministic": True,
    },
]


def export_input_filter_chain_manifest() -> dict[str, Any]:
    return {
        "filters": list(INPUT_FILTER_CHAIN),
        "execution_order": "sequential_strict",
        "audit_trace_required": True,
        "direct_agent_provider_bypass": False,
    }


_INJECTION_MARKERS = ("ignore previous", "override policy", "system_prompt leak")


def assess_input_payload(text: str) -> dict[str, Any]:
    """Deterministic assessment only — no network or model execution."""
    lowered = text.strip().lower()
    if any(m in lowered for m in _INJECTION_MARKERS):
        return {"allowed": False, "blocked_by": "prompt_injection_scan", "deterministic": True}
    return {"allowed": True, "blocked_by": None, "deterministic": True}


def validate_input_filter_id(filter_id: str) -> None:
    known = {f["filter_id"] for f in INPUT_FILTER_CHAIN}
    if filter_id.strip() not in known:
        raise ValueError("invalid input filter id")
