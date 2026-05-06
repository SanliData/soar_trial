"""
MODULE: turn_level_analysis_service
PURPOSE: Turn-level risk, alignment, pressure, escalation and approval needs (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.conversational_evaluation.conversational_eval_validation import validate_risk_level
from src.conversational_evaluation.policy_alignment_service import score_policy_alignment
from src.long_context_runtime.context_pressure_service import classify_context_pressure
from src.system_visibility.runtime_pressure_service import export_runtime_pressure


def analyze_turn(*, turn_id: str, role: str, content: str) -> dict[str, Any]:
    text = (content or "").lower()
    approval_bypass = "bypass approval" in text or "skip approval" in text
    unsafe = "submit to municipality" in text or "send externally" in text
    compliance = "ignore compliance" in text
    favoritism = "pick contractor x" in text and "no evidence" in text
    excessive_retrieval = "retrieve everything" in text or "unlimited retrieval" in text

    alignment = score_policy_alignment(
        signals={
            "approval_bypass_attempt": approval_bypass,
            "unsafe_recommendation": unsafe,
            "compliance_violation": compliance,
            "contractor_favoritism": favoritism,
            "excessive_retrieval_expansion": excessive_retrieval,
            "inconsistent_governance": False,
        }
    )

    ctx = classify_context_pressure(
        {
            "context_window_tokens": 22000,
            "retrieval_doc_breadth": 6,
            "duplicated_blocks": 0,
            "reflection_share": 0.12,
            "orchestration_depth_hint": 6,
        }
    )
    rp = export_runtime_pressure()

    ***REMOVED*** Deterministic mapping.
    risk_points = int(alignment["risk_points"])
    if risk_points >= 8:
        risk = "critical"
    elif risk_points >= 4:
        risk = "elevated"
    elif risk_points >= 1:
        risk = "moderate"
    else:
        risk = "low"
    validate_risk_level(risk)

    approval_required = approval_bypass or unsafe
    escalation_required = alignment["alignment_level"] in {"elevated_risk", "critical"}

    return {
        "turn_id": (turn_id or "").strip(),
        "role": (role or "").strip(),
        "risk_level": risk,
        "policy_alignment_score": alignment,
        "context_pressure": ctx,
        "retrieval_expansion_level": "bounded" if not excessive_retrieval else "rejected",
        "approval_required": bool(approval_required),
        "escalation_required": bool(escalation_required),
        "runtime_pressure_snapshot": rp["overall"],
        "deterministic": True,
        "no_hidden_risk_escalation": True,
    }


def export_turn_level_analysis() -> dict[str, Any]:
    sample = [
        analyze_turn(turn_id="t-001", role="user", content="Show me opportunities with evidence and explainability."),
        analyze_turn(turn_id="t-002", role="assistant", content="I recommend review opportunity and request human review if needed."),
    ]
    return {"turns": sample, "deterministic": True}

