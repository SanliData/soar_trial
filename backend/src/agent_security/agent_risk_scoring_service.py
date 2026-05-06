"""
MODULE: agent_risk_scoring_service
PURPOSE: Deterministic composite risk score for agent/tool contexts (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_security.prompt_sanitization_service import sanitize_prompt
from src.agent_security.retrieval_sanitization_service import sanitize_retrieval
from src.agent_security.tool_capability_registry import TOOL_REGISTRY


def compute_risk_score(
    prompt_text: str,
    retrieval_sample: str = "",
    requested_tools: list[str] | None = None,
) -> dict[str, Any]:
    """
    Score in [0,100] where higher is riskier. Explainable weighted sum — no ML.
    """
    requested_tools = requested_tools or []
    pr = sanitize_prompt(prompt_text)
    rr = sanitize_retrieval(retrieval_sample, content_type="html") if retrieval_sample.strip() else {"findings": [], "modified": False}

    prompt_hits = len(pr.get("findings") or [])
    retr_hits = len(rr.get("findings") or [])
    zw = 1 if pr.get("hidden_markup_removed") else 0

    external_tools = 0
    unverified = 0
    high_risk_tools = 0
    for name in requested_tools:
        cap = TOOL_REGISTRY.get(name)
        if cap is None:
            unverified += 1
            continue
        if cap.external_execution:
            external_tools += 1
        if cap.trust_level in ("external_unverified", "sandbox_only"):
            unverified += 1
        if cap.risk_level == "high":
            high_risk_tools += 1

    raw = (
        prompt_hits * 12.0
        + retr_hits * 10.0
        + zw * 8.0
        + external_tools * 15.0
        + unverified * 14.0
        + high_risk_tools * 10.0
    )
    score = max(0.0, min(100.0, round(raw, 2)))

    return {
        "risk_score": score,
        "breakdown": {
            "prompt_findings": prompt_hits,
            "retrieval_findings": retr_hits,
            "zero_width_markup_removed": zw,
            "external_execution_tools": external_tools,
            "unverified_or_unknown_tools": unverified,
            "high_risk_tool_components": high_risk_tools,
        },
        "sanitization_preview": {
            "prompt_modified": pr.get("modified"),
            "retrieval_modified": rr.get("modified"),
        },
    }
