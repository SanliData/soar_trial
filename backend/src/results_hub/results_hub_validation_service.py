"""
MODULE: results_hub_validation_service
PURPOSE: Validation rules: no hallucinated data, lineage required, no hidden scoring (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def require_lineage(evidence: list[dict[str, Any]]) -> None:
    if not evidence:
        raise ValueError("evidence required")
    for e in evidence:
        lineage = e.get("source_lineage")
        if not isinstance(lineage, dict) or not lineage.get("source_name") or not lineage.get("source_type"):
            raise ValueError("missing source lineage")


def reject_hidden_scoring(payload: dict[str, Any]) -> None:
    if payload.get("hidden_ranking_logic") is True:
        raise ValueError("hidden ranking logic rejected")
    if payload.get("autonomous_action_execution") is True:
        raise ValueError("autonomous action execution rejected")


def ensure_deterministic(payload: dict[str, Any]) -> None:
    if payload.get("deterministic") is not True:
        raise ValueError("payload must be deterministic")

