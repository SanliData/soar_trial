"""
MODULE: capability_execution_policy
PURPOSE: Explicit execution policy enforcement metadata — no unrestricted execution (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.capability_gateway.mcp_gateway_registry import GATEWAYS

_GLOBAL_POLICY: dict[str, Any] = {
    "global_execution_budget_tokens": 32000,
    "global_rate_limit_rpm": 120,
    "sandbox_required_default": True,
    "escalation_policy": "human_on_budget_exceeded_or_unknown_domain",
    "unrestricted_execution": False,
}

_PER_GATEWAY_OVERRIDES: dict[str, dict[str, Any]] = {
    "browser_intelligence": {
        "allowed_domains": ["*.gov.example", "trusted-catalog.internal"],
        "execution_budget_tokens": 8000,
        "rate_limit_rpm": 30,
        "sandbox_required": True,
        "max_parallel_sessions": 1,
    },
    "procurement_lookup": {
        "allowed_domains": ["procurement-api.internal", "catalog-read.internal"],
        "execution_budget_tokens": 16000,
        "rate_limit_rpm": 60,
        "sandbox_required": True,
        "max_parallel_sessions": 2,
    },
    "contractor_verification": {
        "allowed_domains": ["verification-service.internal"],
        "execution_budget_tokens": 12000,
        "rate_limit_rpm": 45,
        "sandbox_required": True,
        "max_parallel_sessions": 1,
    },
    "gis_enrichment": {
        "allowed_domains": ["geo-api.internal"],
        "execution_budget_tokens": 6000,
        "rate_limit_rpm": 90,
        "sandbox_required": True,
        "max_parallel_sessions": 2,
    },
    "document_extraction": {
        "allowed_domains": [],
        "execution_budget_tokens": 24000,
        "rate_limit_rpm": 40,
        "sandbox_required": True,
        "max_parallel_sessions": 2,
    },
}


def export_execution_policies() -> dict[str, Any]:
    policies = []
    for name in sorted(GATEWAYS.keys()):
        row = dict(_GLOBAL_POLICY)
        row["gateway_name"] = name
        row.update(dict(_PER_GATEWAY_OVERRIDES.get(name, {})))
        policies.append(row)
    return {
        "global_defaults": dict(_GLOBAL_POLICY),
        "per_gateway": policies,
        "policy_version": "h037_v1",
    }
