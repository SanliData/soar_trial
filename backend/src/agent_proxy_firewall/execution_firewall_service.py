"""
MODULE: execution_firewall_service
PURPOSE: Execution boundary protections — deterministic denial metadata (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_EXECUTION_RULES: list[dict[str, Any]] = [
    {"rule_id": "no_mass_actions_without_batch_token", "targets": ["bulk_user_ops"], "effect": "deny"},
    {"rule_id": "no_destructive_without_dual_control", "targets": ["infra_mutation"], "effect": "deny"},
    {"rule_id": "external_submit_requires_signed_payload", "targets": ["vendor_webhook"], "effect": "deny"},
    {"rule_id": "unauthorized_graph_writes", "targets": ["graph_rewrite_unscoped"], "effect": "deny"},
    {"rule_id": "escalation_fence", "targets": ["silent_promotion"], "effect": "deny_and_escalate"},
]


def export_execution_firewall_manifest() -> dict[str, Any]:
    return {
        "rules": list(_EXECUTION_RULES),
        "unrestricted_autonomous_execution": False,
        "hidden_runtime_bypasses": False,
        "deterministic": True,
    }
