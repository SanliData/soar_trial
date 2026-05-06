"""
MODULE: runtime_rule_service
PURPOSE: Modular runtime rule bundles — deterministic merge, no monolithic prompts (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_DOMAIN_RULES: list[dict[str, Any]] = [
    {"rule_id": "dom-ttl-001", "text": "All external calls route through governed capability gateways."},
]

_WORKFLOW_RULES: list[dict[str, Any]] = [
    {"rule_id": "wf-seq-001", "text": "Linearize critical path steps; parallel fan-out capped by workspace policy."},
]

_SECURITY_RULES: list[dict[str, Any]] = [
    {"rule_id": "sec-deny-001", "text": "Deny secret material in workspace memory payloads."},
]

_EVAL_RULES: list[dict[str, Any]] = [
    {"rule_id": "eval-cov-001", "text": "Evaluation artefacts must cite rule ids when blocking execution."},
]

_ORCH_RULES: list[dict[str, Any]] = [
    {"rule_id": "orch-scope-001", "text": "Subagent scopes cannot exceed workspace execution_permissions union."},
]


def export_runtime_rules_manifest() -> dict[str, Any]:
    """
    Deterministic merge: fixed key order buckets, no opaque prompt blobs.
    """
    merged = {
        "domain_rules": list(_DOMAIN_RULES),
        "workflow_rules": list(_WORKFLOW_RULES),
        "security_rules": list(_SECURITY_RULES),
        "evaluation_rules": list(_EVAL_RULES),
        "orchestration_rules": list(_ORCH_RULES),
    }
    counts = {k: len(v) for k, v in merged.items()}
    return {
        "rule_buckets": merged,
        "counts": counts,
        "merge_strategy": "static_concat_v1",
        "monolithic_prompt_loading": False,
    }
