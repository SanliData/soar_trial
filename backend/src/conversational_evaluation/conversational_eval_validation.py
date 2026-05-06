"""
MODULE: conversational_eval_validation
PURPOSE: Validation for conversational evaluation outputs (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def reject_hidden_weighting(payload: dict[str, Any]) -> None:
    if payload.get("hidden_evaluation_weighting") is True:
        raise ValueError("hidden evaluation weighting rejected")
    if payload.get("unrestricted_event_execution") is True:
        raise ValueError("unrestricted event execution rejected")
    if payload.get("autonomous_workflow_completion") is True:
        raise ValueError("autonomous workflow completion rejected")


def validate_alignment_level(level: str) -> None:
    if (level or "").strip() not in {"aligned", "warning", "elevated_risk", "critical"}:
        raise ValueError("invalid alignment level")


def validate_risk_level(level: str) -> None:
    if (level or "").strip() not in {"low", "moderate", "elevated", "critical"}:
        raise ValueError("invalid risk level")

