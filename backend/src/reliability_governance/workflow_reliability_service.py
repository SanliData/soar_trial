"""
MODULE: workflow_reliability_service
PURPOSE: Workflow stability scoring — deterministic (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_workflow_reliability(
    *,
    token_estimate: int = 0,
    retry_count: int = 0,
    delegation_flap_count: int = 0,
    acceptance_failure_ratio: float = 0.0,
    context_rot_score: float = 0.0,
) -> dict[str, Any]:
    te = max(0, int(token_estimate))
    rc = max(0, int(retry_count))
    df = max(0, int(delegation_flap_count))
    af = max(0.0, min(1.0, float(acceptance_failure_ratio)))
    cr = max(0.0, min(1.0, float(context_rot_score)))
    token_pressure = min(1.0, te / 500_000.0)
    retry_pressure = min(1.0, rc / 12.0)
    flap_pressure = min(1.0, df / 8.0)
    reliability = round(
        1.0 - (0.3 * token_pressure + 0.25 * retry_pressure + 0.15 * flap_pressure + 0.2 * af + 0.1 * cr),
        4,
    )
    flags = {
        "token_explosion_risk": token_pressure > 0.65,
        "excessive_retries": retry_pressure > 0.5,
        "unstable_delegation": flap_pressure > 0.45,
        "failed_acceptance_elevated": af > 0.2,
        "context_degradation": cr > 0.55,
    }
    return {
        "workflow_reliability_score": max(0.0, reliability),
        "flags": flags,
        "pressures": {
            "token": round(token_pressure, 4),
            "retry": round(retry_pressure, 4),
            "delegation_flap": round(flap_pressure, 4),
        },
        "scoring_rule": "weighted_pressure_v1",
    }
