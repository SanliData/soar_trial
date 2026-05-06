"""
MODULE: nl_command_parser
PURPOSE: Deterministic NL command parsing to intent metadata (no execution) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
from typing import Any


def _summarize(raw: str, max_len: int = 220) -> str:
    s = (raw or "").strip().replace("\n", " ")
    if len(s) <= max_len:
        return s
    return s[: max_len - 20].rstrip() + " …[truncated]"


def parse_nl_command(raw_command: str) -> dict[str, Any]:
    """
    Deterministic parser with conservative, explainable rules.
    This does not execute anything; it produces metadata only.
    """
    raw = (raw_command or "").strip()
    lowered = raw.lower()

    parsed_intent = "unknown"
    workflow_scope = None
    target_agent_type = None
    risk_level = "low"
    recommended_action = "respond_with_metadata_only"

    if any(k in lowered for k in ("procurement", "bid", "rfp", "vendor")):
        parsed_intent = "procurement_analysis"
        workflow_scope = "procurement_analysis"
        target_agent_type = "procurement_agent"
    elif any(k in lowered for k in ("contractor", "license", "insurance")):
        parsed_intent = "contractor_ranking"
        workflow_scope = "contractor_ranking"
        target_agent_type = "contractor_intelligence_agent"
    elif any(k in lowered for k in ("permit", "inspection", "violation")):
        parsed_intent = "permit_monitoring"
        workflow_scope = "permit_monitoring"
        target_agent_type = "permit_monitoring_agent"
    elif any(k in lowered for k in ("onboarding", "checklist", "policy pack")):
        parsed_intent = "onboarding_generation"
        workflow_scope = "onboarding_generation"
        target_agent_type = "onboarding_agent"
    elif any(k in lowered for k in ("executive", "board", "briefing")):
        parsed_intent = "executive_reporting"
        workflow_scope = "executive_reporting"
        target_agent_type = "executive_reporting_agent"
    elif any(k in lowered for k in ("graph", "relationship", "network")):
        parsed_intent = "graph_investigation"
        workflow_scope = "graph_investigation"
        target_agent_type = "graph_investigation_agent"

    # High-risk trigger phrases (metadata only)
    high_risk_markers = ("submit", "export", "delete", "rewrite graph", "deploy", "production", "escalate")
    if any(m in lowered for m in high_risk_markers):
        risk_level = "high"
        recommended_action = "require_human_approval_and_generate_plan"

    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16] if raw else "empty"
    return {
        "raw_command": raw,
        "raw_command_summary": _summarize(raw),
        "parsed_intent": parsed_intent,
        "target_agent_type": target_agent_type,
        "workflow_scope": workflow_scope,
        "risk_level": risk_level,
        "human_approval_required": risk_level in {"high", "critical"},
        "recommended_action": recommended_action,
        "deterministic": True,
        "command_digest": digest,
        "no_execution": True,
    }

