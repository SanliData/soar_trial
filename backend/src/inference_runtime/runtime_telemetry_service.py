"""
MODULE: runtime_telemetry_service
PURPOSE: Explainable deterministic telemetry shapes (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.context_compression.context_token_optimizer import export_context_token_optimizer_manifest
from src.agent_operating_system.agent_fleet_service import export_agent_fleet_status
from src.federated_retrieval.retrieval_observability_service import export_retrieval_observability
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion
from src.hardware_aware_runtime.runtime_hardware_router import route_workload
from src.hardware_aware_runtime.hardware_cost_service import export_hardware_costs
from src.adaptive_clustering.cluster_utility_service import export_cluster_utility
from src.prompt_cache_governance.cache_efficiency_service import export_cache_efficiency
from src.prompt_cache_governance.cache_breakpoint_service import export_cache_breakpoints
from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry
from src.prompt_cache_governance.cache_safe_compression_service import export_cache_safe_compression
from src.long_context_runtime.h043_inference_hooks import (
    export_ensemble_budget_cross_hint,
    export_inference_governance_addon,
    trimmed_sparse_providers_for_inference,
)

_CANONICAL_TELEMETRY: dict[str, Any] = {
    "workflow_latency_ms_p50": 420,
    "workflow_latency_ms_p95": 1800,
    "token_usage": {"input": 9200, "output": 2100},
    "batching_efficiency": 0.78,
    "retry_counts": {"transient_provider": 1, "application": 0},
    "orchestration_depth": 3,
    "context_load_size_tokens": 14500,
    "reflection_ratio": 0.12,
    "retrieval_ratio": 0.21,
    "long_context_telemetry_hook_schema": "h043_inference_bridge_v1",
    "adaptive_context_load_signal": "importance_weighted_partition_first",
    # H-044 typed context telemetry hooks (deterministic only)
    "context_token_cost": 0,
    "compression_savings": 0,
    "duplicate_context_waste": 0,
    "prefill_pressure_from_context": 0.0,
    # H-045 signals (deterministic metadata only)
    "selective_context_token_savings": 0,
    "retrieval_expansion_pressure": 0.0,
    "federated_retrieval_cost_metadata": {"connector_count": 0, "stale_connector_count": 0},
    "agent_fleet_runtime_pressure": {"high_risk_agents": 0, "paused_agents": 0},
}


def export_runtime_telemetry_manifest() -> dict[str, Any]:
    ctx = export_context_token_optimizer_manifest()
    sample = dict(_CANONICAL_TELEMETRY)
    sample["context_token_cost"] = int(ctx.get("context_token_cost") or 0)
    sample["compression_savings"] = int(ctx.get("compression_savings") or 0)
    sample["duplicate_context_waste"] = int(ctx.get("duplicate_context_waste") or 0)
    sample["prefill_pressure_from_context"] = float(ctx.get("prefill_pressure_from_context") or 0.0)
    # H-045 derived sample metrics
    fleet = export_agent_fleet_status()
    retrieval = export_retrieval_observability()
    expansion = decide_selective_expansion(
        workflow_name="procurement_analysis",
        query="ISO 27001 net-30",
        chunks=[
            {"chunk_id": "c1", "text": "ISO 27001 net-30", "source_lineage": {"authority_score": 0.88, "freshness_days": 3}},
            {"chunk_id": "c2", "text": "marketing", "source_lineage": {"authority_score": 0.55, "freshness_days": 21}},
        ],
    )
    sample["selective_context_token_savings"] = int(expansion.get("token_savings_estimate") or 0)
    sample["retrieval_expansion_pressure"] = round(
        min(1.0, (float(ctx.get("prefill_pressure_from_context") or 0.0) + 0.15)), 4
    )
    sample["federated_retrieval_cost_metadata"] = {
        "connector_count": int(retrieval["connector_count"]),
        "stale_connector_count": int(retrieval["stale_connector_count"]),
    }
    sample["agent_fleet_runtime_pressure"] = {
        "high_risk_agents": int(fleet["high_risk_agents"]),
        "paused_agents": int(fleet["paused_agents"]),
    }
    # H-050 cache governance telemetry (deterministic, explainable)
    cache_eff = export_cache_efficiency()["cache_efficiency"]
    sample["cache_efficiency_ratio"] = float(cache_eff["cache_efficiency_ratio"])
    sample["cache_read_input_tokens"] = int(cache_eff["cache_read_input_tokens"])
    sample["cache_creation_input_tokens"] = int(cache_eff["cache_creation_input_tokens"])
    sample["prefill_saved_tokens"] = int(cache_eff["estimated_prefill_saved_tokens"])
    sample["cache_breakpoint_validity"] = export_cache_breakpoints(session_id="sess-demo-001")["breakpoints"][0]["cache_valid"]
    sample["static_prefix_stability"] = export_static_prefix_registry()["static_prefix_stable"]
    sample["cache_safe_compression_telemetry"] = export_cache_safe_compression(session_id="sess-demo-001")
    # H-049 hardware-aware + clustering telemetry (metadata only)
    sample["hardware_routing_hint"] = route_workload(workload="orchestration")
    sample["hardware_cost_intelligence"] = export_hardware_costs()
    sample["adaptive_clustering_telemetry"] = {"utility": export_cluster_utility(), "deterministic": True}
    return {
        "sample_snapshot": sample,
        "h043_long_context_integration": export_inference_governance_addon(),
        "h043_sparse_runtime_cross_ref": trimmed_sparse_providers_for_inference(),
        "h043_ensemble_budget_hint": export_ensemble_budget_cross_hint(),
        "schema_version": "h041_runtime_telemetry_v2_h043",
        "auditable": True,
        "deterministic": True,
    }
