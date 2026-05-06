"""
MODULE: human_approval_service
PURPOSE: Deterministic classification of approval-required operations (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

APPROVAL_REQUIRED_INTENTS = frozenset(
    {
        "external_submission",
        "bulk_export",
        "graph_rewrite",
        "agent_creation",
        "capability_escalation",
        "production_workflow_mutation",
    }
)


def classify_approval_requirement(*, parsed_intent: str, risk_level: str) -> dict[str, Any]:
    intent = (parsed_intent or "").strip()
    risk = (risk_level or "").strip().lower()

    required = False
    reasons: list[str] = []

    if intent in APPROVAL_REQUIRED_INTENTS:
        required = True
        reasons.append("approval_required_intent")

    if risk in {"high", "critical"}:
        required = True
        reasons.append("risk_level_requires_approval")

    return {
        "human_approval_required": required,
        "reasons": sorted(set(reasons)),
        "approval_policy": "explicit_metadata_only_no_auto_approval",
        "deterministic": True,
    }

