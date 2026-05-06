"""
MODULE: runtime_collapse_detection_service
PURPOSE: Collapse classifications — detection only (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_THRESHOLDS = {
    "runaway_workflow_steps": 50,
    "retry_storm_count": 8,
    "orchestration_depth_max": 12,
    "token_explosion_input": 120000,
    "unsafe_parallelism_active": 8,
    "orchestration_flood_rps": 25.0,
}


def assess_runtime_collapse_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministic rule engine over numeric hints. Does not mutate execution.
    """
    flags: list[str] = []

    steps = int(snapshot.get("workflow_step_count") or 0)
    if steps > _THRESHOLDS["runaway_workflow_steps"]:
        flags.append("runaway_workflows")

    retries = int(snapshot.get("retry_count_windowed") or 0)
    if retries > _THRESHOLDS["retry_storm_count"]:
        flags.append("retry_storms")

    depth = int(snapshot.get("orchestration_depth") or 0)
    if depth > _THRESHOLDS["orchestration_depth_max"]:
        flags.append("recursive_orchestration_risk")

    tok_in = int(snapshot.get("token_input_recent") or 0)
    if tok_in > _THRESHOLDS["token_explosion_input"]:
        flags.append("token_explosions")

    par = int(snapshot.get("active_parallelism") or 0)
    if par > _THRESHOLDS["unsafe_parallelism_active"]:
        flags.append("unsafe_parallelism_spike")

    rps = float(snapshot.get("orchestration_invoke_rps") or 0.0)
    if rps > _THRESHOLDS["orchestration_flood_rps"]:
        flags.append("orchestration_floods")

    if flags:
        level = "critical" if len(flags) >= 3 or "token_explosions" in flags else "high"
    else:
        level = "nominal"

    return {
        "collapse_risk_level": level,
        "flags": sorted(flags),
        "thresholds_exposed": dict(_THRESHOLDS),
        "autonomous_shutdown": False,
        "detection_only": True,
        "explainable_classifications": True,
        "deterministic": True,
    }


def export_collapse_detection_manifest() -> dict[str, Any]:
    return {
        "thresholds": dict(_THRESHOLDS),
        "example_nominal": assess_runtime_collapse_risk(
            {
                "workflow_step_count": 5,
                "retry_count_windowed": 1,
                "orchestration_depth": 3,
                "token_input_recent": 8000,
                "active_parallelism": 2,
                "orchestration_invoke_rps": 2.0,
            }
        ),
        "example_critical": assess_runtime_collapse_risk(
            {
                "workflow_step_count": 120,
                "retry_count_windowed": 14,
                "orchestration_depth": 14,
                "token_input_recent": 150000,
                "active_parallelism": 14,
                "orchestration_invoke_rps": 40.0,
            }
        ),
        "deterministic": True,
    }
