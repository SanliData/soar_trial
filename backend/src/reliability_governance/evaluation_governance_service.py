"""
MODULE: evaluation_governance_service
PURPOSE: Evaluation reliability governance — deterministic checks (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.conversational_evaluation.evaluation_session_registry import export_sessions


def export_evaluation_governance(
    *,
    suite_version_age_days: float = 0.0,
    missing_coverage_ratio: float = 0.0,
    comparison_weak_ratio: float = 0.0,
    inconsistent_run_ratio: float = 0.0,
) -> dict[str, Any]:
    mc = max(0.0, min(1.0, float(missing_coverage_ratio)))
    cw = max(0.0, min(1.0, float(comparison_weak_ratio)))
    ir = max(0.0, min(1.0, float(inconsistent_run_ratio)))
    stale = float(suite_version_age_days) > 30.0
    governance_score = round(1.0 - (0.35 * mc + 0.35 * cw + 0.3 * ir), 4)
    conv = export_sessions(limit=25)
    return {
        "evaluation_consistency_warning": ir > 0.15,
        "missing_coverage_elevated": mc > 0.2,
        "stale_evaluation_logic": stale,
        "weak_comparison_quality": cw > 0.25,
        "governance_score": max(0.0, governance_score),
        ***REMOVED*** H-048 integration (metadata only): conversational evaluation visibility
        "conversational_sessions_visible": True,
        "conversational_session_count": int(conv.get("session_count") or 0),
        "metadata": {
            "suite_version_age_days": float(suite_version_age_days),
            "rules": "weighted_penalty_v1",
            "deterministic": True,
        },
    }
