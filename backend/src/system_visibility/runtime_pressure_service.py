"""
MODULE: runtime_pressure_service
PURPOSE: Token/context/orchestration/retrieval/agent/retry pressure (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_fleet_service import export_agent_fleet_status
from src.federated_retrieval.retrieval_observability_service import export_retrieval_observability
from src.inference_runtime.runtime_telemetry_service import export_runtime_telemetry_manifest
from src.long_context_runtime.context_pressure_service import classify_context_pressure
from src.system_visibility.visibility_validation_service import validate_pressure_level


def _classify_pressure(score: int) -> str:
    if score <= 1:
        return "healthy"
    if score <= 3:
        return "elevated"
    if score <= 6:
        return "high"
    return "critical"


def export_runtime_pressure() -> dict[str, Any]:
    telemetry = export_runtime_telemetry_manifest()["sample_snapshot"]
    fleet = export_agent_fleet_status()
    retrieval = export_retrieval_observability()

    token_load = int(telemetry.get("context_load_size_tokens") or 0)
    orchestration_depth = int(telemetry.get("orchestration_depth") or 0)
    retry_total = int(sum((telemetry.get("retry_counts") or {}).values())) if isinstance(telemetry.get("retry_counts"), dict) else 0

    token_score = 0
    if token_load > 64000:
        token_score = 3
    elif token_load > 32000:
        token_score = 2
    elif token_load > 16000:
        token_score = 1

    context_pressure = classify_context_pressure(
        {
            "context_window_tokens": token_load,
            "retrieval_doc_breadth": 8,
            "duplicated_blocks": int(telemetry.get("duplicate_context_waste") or 0) // 1000,
            "reflection_share": float(telemetry.get("reflection_ratio") or 0.0),
            "orchestration_depth_hint": orchestration_depth,
        }
    )
    ctx_level = context_pressure["pressure_level"]
    ctx_score = {"low": 0, "moderate": 1, "high": 2, "critical": 3}.get(ctx_level, 1)

    orch_score = 2 if orchestration_depth > 10 else 1 if orchestration_depth > 6 else 0
    retrieval_score = 2 if int(retrieval.get("stale_connector_count") or 0) > 2 else 1 if int(retrieval.get("retrieval_warning_count") or 0) > 0 else 0
    fleet_score = 2 if int(fleet.get("high_risk_agents") or 0) >= 4 else 1 if int(fleet.get("paused_agents") or 0) > 0 else 0
    retry_score = 2 if retry_total >= 4 else 1 if retry_total >= 2 else 0

    pressures = {
        "token_pressure": {"score": token_score, "level": _classify_pressure(token_score), "explain": "context_load_size_tokens thresholds"},
        "context_pressure": {"score": ctx_score, "level": "critical" if ctx_level == "critical" else "high" if ctx_level == "high" else "elevated" if ctx_level == "moderate" else "healthy", "explain": "H-043 context pressure classifier"},
        "orchestration_pressure": {"score": orch_score, "level": _classify_pressure(orch_score), "explain": "orchestration_depth thresholds"},
        "retrieval_pressure": {"score": retrieval_score, "level": _classify_pressure(retrieval_score), "explain": "stale connectors and warnings"},
        "agent_fleet_pressure": {"score": fleet_score, "level": _classify_pressure(fleet_score), "explain": "high-risk + paused agents"},
        "retry_pressure": {"score": retry_score, "level": _classify_pressure(retry_score), "explain": "retry_counts sum thresholds"},
    }
    for p in pressures.values():
        validate_pressure_level(p["level"])

    total_score = sum(int(p["score"]) for p in pressures.values())
    overall = _classify_pressure(total_score // 2)
    validate_pressure_level(overall)

    return {
        "pressures": pressures,
        "overall": {"score": total_score, "level": overall, "deterministic": True},
        "deterministic": True,
        "thresholds_explainable": True,
    }

