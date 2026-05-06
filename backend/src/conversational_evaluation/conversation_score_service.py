"""
MODULE: conversation_score_service
PURPOSE: Deterministic aggregate conversation scoring (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def aggregate_conversation_score(*, turn_analyses: list[dict[str, Any]], alignment: dict[str, Any]) -> dict[str, Any]:
    """
    No hidden evaluation weighting: simple deterministic aggregation.
    """
    risk_points = 0
    risk_points += int(alignment.get("risk_points") or 0)
    for t in turn_analyses:
        if t.get("risk_level") == "critical":
            risk_points += 4
        elif t.get("risk_level") == "elevated":
            risk_points += 2
        elif t.get("risk_level") == "moderate":
            risk_points += 1

    if risk_points == 0:
        level = "healthy"
    elif risk_points <= 3:
        level = "elevated"
    elif risk_points <= 7:
        level = "high"
    else:
        level = "critical"

    return {
        "conversation_risk_points": int(risk_points),
        "conversation_risk_level": level,
        "deterministic": True,
        "hidden_evaluation_weighting": False,
    }

