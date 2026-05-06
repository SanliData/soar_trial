"""
MODULE: trace_to_eval_service
PURPOSE: Deterministic trace → evaluation rule mapping — no self-modification (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

# (trace_category, trace_code) → structured evaluation artifacts.
_TRACE_EVAL_RULES: dict[tuple[str, str], dict[str, Any]] = {
    ("hallucinated_outputs", "contractor_fit"): {
        "evaluation_heuristic": "require_two_independent_sources",
        "validation_rules": ["ban_uncited_numeric_claims", "require_primary_source_tag"],
        "governance_recommendations": ["enable_retrieval_attribution_gate"],
    },
    ("unstable_graph_reasoning", "generic"): {
        "evaluation_heuristic": "relative_path_stability_score",
        "validation_rules": ["max_hop_variance_bucket", "freeze_evidence_set"],
        "governance_recommendations": ["reduce_parallel_graph_queries"],
    },
    ("workflow_failure", "acceptance"): {
        "evaluation_heuristic": "contract_key_coverage",
        "validation_rules": ["fail_closed_on_missing_keys"],
        "governance_recommendations": ["tighten_delegation_depth_cap"],
    },
    ("retrieval_mismatch", "generic"): {
        "evaluation_heuristic": "chunk_hash_consistency",
        "validation_rules": ["reindex_on_drift_signal"],
        "governance_recommendations": ["raise_retrieval_quality_alert"],
    },
    ("invalid_orchestration", "generic"): {
        "evaluation_heuristic": "capability_allowlist_diff",
        "validation_rules": ["reject_unknown_capability_ids"],
        "governance_recommendations": ["refresh_planner_manifest_cache"],
    },
}


def map_trace_to_eval(trace_category: str, trace_code: str = "generic") -> dict[str, Any]:
    key = (trace_category.strip().lower(), trace_code.strip().lower())
    if key not in _TRACE_EVAL_RULES:
        key = (trace_category.strip().lower(), "generic")
    if key not in _TRACE_EVAL_RULES:
        raise ValueError(f"unknown trace mapping: {trace_category}/{trace_code}")
    payload = dict(_TRACE_EVAL_RULES[key])
    return {
        "mapping_rule": "static_lookup_v1",
        "trace_category": trace_category,
        "trace_code": trace_code,
        **payload,
        "autonomous_rule_mutation": False,
    }
