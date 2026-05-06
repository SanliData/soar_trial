"""
MODULE: inference_validation_service
PURPOSE: Validate budgets, batching, parallelism, speculative, cache, telemetry, collapse (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_VALID_BUDGET_CATEGORIES = frozenset(
    {"orchestration", "reflection", "evaluation", "skill_activation", "retrieval", "graph_reasoning", "ensemble_evaluation"}
)
_REQUIRED_TELEMETRY_KEYS = frozenset(
    {
        "workflow_latency_ms_p50",
        "token_usage",
        "batching_efficiency",
        "retry_counts",
        "orchestration_depth",
        "context_load_size_tokens",
        "reflection_ratio",
        "retrieval_ratio",
    }
)


def validate_token_budget_category(category: str) -> None:
    if category.strip() not in _VALID_BUDGET_CATEGORIES:
        raise ValueError("invalid token budget category")


def validate_batching_metadata(row: dict[str, Any]) -> None:
    required = {"workflow_group_id", "batching_eligible"}
    if required - row.keys():
        raise ValueError("invalid batching metadata")


def validate_parallelism_config(cfg: dict[str, Any]) -> None:
    for k in ("max_parallel_workflows", "token_concurrency_cap", "max_retry_concurrency"):
        v = cfg.get(k)
        if not isinstance(v, int) or v < 1:
            raise ValueError("invalid parallelism config")


def validate_speculative_metadata(meta: dict[str, Any]) -> None:
    if meta.get("uncontrolled_speculative_execution") is True:
        raise ValueError("unsafe speculative metadata")
    if meta.get("autonomous_commit") is True:
        raise ValueError("unsafe speculative metadata")


def validate_kv_cache_entry(entry: dict[str, Any]) -> None:
    if "workflow_name" not in entry or "reuse_allowed" not in entry:
        raise ValueError("invalid kv cache entry")


def validate_telemetry_structure(snapshot: dict[str, Any]) -> None:
    if _REQUIRED_TELEMETRY_KEYS - snapshot.keys():
        raise ValueError("invalid telemetry structure")


def validate_collapse_thresholds(thresholds: dict[str, Any]) -> None:
    if int(thresholds.get("retry_storm_count") or 0) < 1:
        raise ValueError("unsafe collapse thresholds")


def validate_uncontrolled_runtime_expansion_flag(manifest: dict[str, Any]) -> None:
    if manifest.get("uncontrolled_runtime_expansion") is True:
        raise ValueError("uncontrolled runtime expansion not allowed")
