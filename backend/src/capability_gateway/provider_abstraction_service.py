"""
MODULE: provider_abstraction_service
PURPOSE: Unified provider metadata and deterministic selection — no hidden failover (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

PROVIDER_TYPES = frozenset({"openai", "anthropic", "ollama", "local_llm", "vllm_future"})

_PROVIDER_CAPS: dict[str, dict[str, Any]] = {
    "openai": {"streaming": True, "tool_calls": True, "batch": True, "hosted": True},
    "anthropic": {"streaming": True, "tool_calls": True, "batch": False, "hosted": True},
    "ollama": {"streaming": True, "tool_calls": False, "batch": False, "hosted": False},
    "local_llm": {"streaming": True, "tool_calls": False, "batch": False, "hosted": False},
    "vllm_future": {"streaming": True, "tool_calls": True, "batch": True, "hosted": False},
}

# H-043 sparse / long-context metadata — informational only; no auto-switching.
_PROVIDER_SPARSE_METADATA: dict[str, dict[str, Any]] = {
    "openai": {
        "sparse_moe": True,
        "active_parameter_count": 44_000_000_000,
        "long_context_support": True,
        "total_parameter_count_claim": 1_760_000_000_000,
        "context_efficiency_score": 0.82,
        "reasoning_profile": "dense_aux_routing",
        "provider_auto_switching": False,
    },
    "anthropic": {
        "sparse_moe": False,
        "active_parameter_count": None,
        "long_context_support": True,
        "total_parameter_count_claim": None,
        "context_efficiency_score": 0.79,
        "reasoning_profile": "long_context_dense",
        "provider_auto_switching": False,
    },
    "ollama": {
        "sparse_moe": False,
        "active_parameter_count": None,
        "long_context_support": False,
        "total_parameter_count_claim": None,
        "context_efficiency_score": 0.68,
        "reasoning_profile": "single_expert_local",
        "provider_auto_switching": False,
    },
    "local_llm": {
        "sparse_moe": False,
        "active_parameter_count": 8_000_000_000,
        "long_context_support": True,
        "total_parameter_count_claim": 8_000_000_000,
        "context_efficiency_score": 0.71,
        "reasoning_profile": "single_expert",
        "provider_auto_switching": False,
    },
    "vllm_future": {
        "sparse_moe": True,
        "active_parameter_count": None,
        "long_context_support": True,
        "total_parameter_count_claim": None,
        "context_efficiency_score": 0.74,
        "reasoning_profile": "cluster_moe_optional",
        "provider_auto_switching": False,
    },
}

_PROVIDER_RESTRICTIONS: dict[str, dict[str, Any]] = {
    "openai": {"egress": "managed_vendor", "data_residency": "policy_runtime", "max_chain_depth": 1},
    "anthropic": {"egress": "managed_vendor", "data_residency": "policy_runtime", "max_chain_depth": 1},
    "ollama": {"egress": "loopback_only", "data_residency": "on_device", "max_chain_depth": 1},
    "local_llm": {"egress": "disabled", "data_residency": "on_device", "max_chain_depth": 1},
    "vllm_future": {"egress": "internal_lb_only", "data_residency": "tenant_cluster", "max_chain_depth": 1},
}

# task_profile -> deterministic routing (explainable; single rule match).
_ROUTING_TABLE: dict[str, tuple[str, str]] = {
    "default": ("local_llm", "prefer_local_first_privacy"),
    "privacy_strict": ("local_llm", "privacy_strict_profile"),
    "hosted_quality": ("openai", "policy_allows_managed_host"),
    "reasoning_heavy": ("anthropic", "reasoning_route_static"),
    "edge_low_latency": ("ollama", "loopback_latency_route"),
    "future_cluster": ("vllm_future", "reserved_future_slot"),
}


def get_provider_capabilities(provider_type: str) -> dict[str, Any]:
    key = provider_type.strip().lower()
    if key not in _PROVIDER_CAPS:
        raise ValueError("unknown provider type")
    return {"provider_type": key, "capabilities": dict(_PROVIDER_CAPS[key])}


def get_provider_restrictions(provider_type: str) -> dict[str, Any]:
    key = provider_type.strip().lower()
    if key not in _PROVIDER_RESTRICTIONS:
        raise ValueError("unknown provider type")
    return {"provider_type": key, "restrictions": dict(_PROVIDER_RESTRICTIONS[key])}


def select_provider(task_profile: str) -> dict[str, Any]:
    """
    Deterministic selection — first exact match on routing table, else default row.
    """
    prof = task_profile.strip().lower()
    rule_id = "fallback_default"
    if prof in _ROUTING_TABLE:
        provider, explain = _ROUTING_TABLE[prof]
        rule_id = f"route:{prof}"
    else:
        provider, explain = _ROUTING_TABLE["default"]
        explain = f"{explain}; profile_not_in_table_using_default"
    return {
        "routing_rule": "static_table_v1",
        "routing_rule_id": rule_id,
        "selected_provider": provider,
        "explain": explain,
        "hidden_failover": False,
        "deterministic": True,
    }


def export_providers_surfaces() -> dict[str, Any]:
    return {
        "provider_types": sorted(PROVIDER_TYPES),
        "routing_profiles": sorted(_ROUTING_TABLE.keys()),
        "capabilities_by_provider": {k: dict(v) for k, v in sorted(_PROVIDER_CAPS.items())},
        "restrictions_by_provider": {k: dict(v) for k, v in sorted(_PROVIDER_RESTRICTIONS.items())},
        "sparse_long_context_metadata_by_provider": {k: dict(v) for k, v in sorted(_PROVIDER_SPARSE_METADATA.items())},
        "metadata_only_no_auto_switch": True,
    }
