"""
MODULE: output_filter_chain_service
PURPOSE: Outbound model-output filter chain — interception before agent execution (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

OUTPUT_FILTER_CHAIN: list[dict[str, Any]] = [
    {
        "filter_id": "destructive_command_scan",
        "sequence": 1,
        "checks": ["rm_rf_patterns", "sql_drop_patterns", "mass_delete_tokens"],
        "violations_action": "block_and_trace",
        "deterministic": True,
    },
    {
        "filter_id": "browser_action_scan",
        "sequence": 2,
        "checks": ["unscoped_navigate", "credential_autofill_hints"],
        "violations_action": "block_and_escalate",
        "deterministic": True,
    },
    {
        "filter_id": "workflow_mutation_scan",
        "sequence": 3,
        "checks": ["silent_policy_override_hints", "ungoverned_orchestration_directives"],
        "violations_action": "block_and_escalate",
        "deterministic": True,
    },
]


def export_output_filter_chain_manifest() -> dict[str, Any]:
    return {
        "filters": list(OUTPUT_FILTER_CHAIN),
        "execution_order": "sequential_strict",
        "output_interception_required": True,
        "uncontrolled_browser_execution": False,
        "audit_trace_required": True,
    }


_DANGEROUS_OUTPUT_MARKERS = ("rm -rf /", "drop database", "mass_delete all", "unscoped_browser_navigate")


def assess_output_payload(text: str) -> dict[str, Any]:
    lowered = text.strip().lower()
    if any(m in lowered for m in _DANGEROUS_OUTPUT_MARKERS):
        return {"blocked": True, "blocked_by": "destructive_command_scan", "deterministic": True}
    return {"blocked": False, "blocked_by": None, "deterministic": True}


def validate_output_filter_id(filter_id: str) -> None:
    known = {f["filter_id"] for f in OUTPUT_FILTER_CHAIN}
    if filter_id.strip() not in known:
        raise ValueError("invalid output filter id")
