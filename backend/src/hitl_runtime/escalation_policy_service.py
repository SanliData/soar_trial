"""
MODULE: escalation_policy_service
PURPOSE: Deterministic escalation policies (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def classify_escalation(*, signals: dict[str, Any]) -> dict[str, Any]:
    s = dict(signals or {})
    repeated_unsafe = int(s.get("repeated_unsafe_outputs") or 0)
    policy_drift = bool(s.get("policy_drift"))
    inconsistent = bool(s.get("inconsistent_recommendations"))
    excessive_retrieval = int(s.get("excessive_retrieval_expansion") or 0)

    points = 0
    points += min(4, repeated_unsafe)
    points += 3 if policy_drift else 0
    points += 2 if inconsistent else 0
    points += min(3, excessive_retrieval)

    if points <= 1:
        level = "low"
    elif points <= 3:
        level = "moderate"
    elif points <= 6:
        level = "elevated"
    else:
        level = "critical"
    return {"escalation_level": level, "points": int(points), "signals": s, "deterministic": True, "explainable": True}


def export_escalations() -> dict[str, Any]:
    return classify_escalation(
        signals={"repeated_unsafe_outputs": 0, "policy_drift": False, "inconsistent_recommendations": False, "excessive_retrieval_expansion": 0}
    )
