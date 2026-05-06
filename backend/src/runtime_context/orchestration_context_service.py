"""
MODULE: orchestration_context_service
PURPOSE: Orchestration-ready hints bundle from metadata (H-030)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.runtime_context.backend_metadata_service import build_backend_metadata_snapshot
from src.context_compression.context_token_optimizer import export_context_token_optimizer_manifest
from src.context_orchestration.context_validation_service import ALLOWED_CONTEXT_TYPES
from src.agent_operating_system.agent_fleet_service import export_agent_fleet_status
from src.federated_retrieval.retrieval_observability_service import export_retrieval_observability
from src.selective_context_runtime.retrieval_budget_service import export_retrieval_budgets


def build_orchestration_context() -> dict[str, Any]:
    meta = build_backend_metadata_snapshot()
    security_escalation = meta.get("security_status") == "requires_review"
    context_opt = export_context_token_optimizer_manifest()
    fleet = export_agent_fleet_status()
    retrieval_obs = export_retrieval_observability()
    budgets = export_retrieval_budgets()
    return {
        "preferred_prompt_strategy": "json_prompting",
        "graph_available": meta.get("graph_status") == "available",
        "ingestion_freshness": "ok" if meta.get("ingestion_status") == "enabled" else "degraded",
        "widget_rendering_available": meta.get("widget_status") == "enabled",
        "security_escalation_required": security_escalation,
        "typed_context_integration": {
            "enabled": True,
            "typed_context_types": sorted(ALLOWED_CONTEXT_TYPES),
            "guardrails_visible_separately": True,
            "token_budget_aware": True,
            "context_token_cost": context_opt.get("context_token_cost"),
            "compression_savings": context_opt.get("compression_savings"),
            "duplicate_context_waste": context_opt.get("duplicate_context_waste"),
            "prefill_pressure_from_context": context_opt.get("prefill_pressure_from_context"),
            "no_global_prompt_blob": True,
        },
        "agent_os_summary": {
            "total_agents": fleet["total_agents"],
            "active_agents": fleet["active_agents"],
            "paused_agents": fleet["paused_agents"],
            "high_risk_agents": fleet["high_risk_agents"],
            "governance_warnings": list(fleet.get("governance_warnings") or []),
            "deterministic": True,
        },
        "retrieval_fabric_summary": {
            "connector_count": retrieval_obs["connector_count"],
            "stale_connector_count": retrieval_obs["stale_connector_count"],
            "retrieval_warning_count": retrieval_obs["retrieval_warning_count"],
            "deterministic": True,
        },
        "selective_context_budget_summary": {
            "workflow_budgets": len(budgets["budgets"]),
            "explicit_limits": True,
            "deterministic": True,
        },
        "notes": "deterministic_bundle_v1",
    }


def build_runtime_bundle() -> dict[str, Any]:
    meta = build_backend_metadata_snapshot()
    orch = build_orchestration_context()
    return {"backend_metadata": meta, "orchestration_context": orch}
