"""
MODULE: conversation_eval_service
PURPOSE: Multi-turn conversational evaluation sessions with governance checks (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.conversational_evaluation.conversation_score_service import aggregate_conversation_score
from src.conversational_evaluation.conversational_eval_validation import reject_hidden_weighting
from src.conversational_evaluation.evaluation_session_registry import append_turn, create_session, export_sessions, set_policy_status
from src.conversational_evaluation.multi_turn_trace_service import append_trace_event
from src.conversational_evaluation.policy_alignment_service import score_policy_alignment
from src.conversational_evaluation.turn_level_analysis_service import analyze_turn


def run_conversation_evaluation(
    *,
    session_id: str,
    workflow_scope: str,
    evaluation_type: str,
    turns: list[dict[str, Any]],
) -> dict[str, Any]:
    sess = create_session(session_id=session_id, workflow_scope=workflow_scope, evaluation_type=evaluation_type)
    turn_analyses = []
    for idx, t in enumerate(turns, start=1):
        turn_id = t.get("turn_id") or f"turn-{idx:03d}"
        role = t.get("role") or "user"
        content = t.get("content") or ""
        append_turn(session_id=session_id, turn_id=str(turn_id), role=str(role), content=str(content))
        analysis = analyze_turn(turn_id=str(turn_id), role=str(role), content=str(content))
        turn_analyses.append(analysis)
        append_trace_event(session_id=session_id, event_type="TURN_ANALYZED", source_service="turn_level_analysis_service", payload=analysis)

    # Conversation alignment is aggregate of turn-level signals (simple deterministic).
    any_bypass = any(a["policy_alignment_score"]["signals"]["approval_bypass_attempt"] for a in turn_analyses)
    any_unsafe = any(a["policy_alignment_score"]["signals"]["unsafe_recommendation"] for a in turn_analyses)
    any_compliance = any(a["policy_alignment_score"]["signals"]["compliance_violation"] for a in turn_analyses)
    any_favor = any(a["policy_alignment_score"]["signals"]["contractor_favoritism"] for a in turn_analyses)
    any_retrieval = any(a["policy_alignment_score"]["signals"]["excessive_retrieval_expansion"] for a in turn_analyses)
    alignment = score_policy_alignment(
        signals={
            "approval_bypass_attempt": any_bypass,
            "unsafe_recommendation": any_unsafe,
            "compliance_violation": any_compliance,
            "contractor_favoritism": any_favor,
            "excessive_retrieval_expansion": any_retrieval,
            "inconsistent_governance": False,
        }
    )
    set_policy_status(session_id=session_id, policy_status=alignment["alignment_level"])
    append_trace_event(session_id=session_id, event_type="POLICY_ALIGNMENT", source_service="policy_alignment_service", payload=alignment)

    score = aggregate_conversation_score(turn_analyses=turn_analyses, alignment=alignment)
    append_trace_event(session_id=session_id, event_type="CONVERSATION_SCORE", source_service="conversation_score_service", payload=score)

    out = {
        "session": sess,
        "turn_analyses": turn_analyses,
        "policy_alignment": alignment,
        "conversation_score": score,
        "deterministic": True,
        "hidden_evaluation_weighting": False,
        "unrestricted_event_execution": False,
        "autonomous_workflow_completion": False,
    }
    reject_hidden_weighting(out)
    return out


def export_conversation_eval_snapshot() -> dict[str, Any]:
    """
    Deterministic demo snapshot.
    """
    return run_conversation_evaluation(
        session_id="sess-demo-001",
        workflow_scope="procurement_analysis",
        evaluation_type="procurement_safety",
        turns=[
            {"turn_id": "t-001", "role": "user", "content": "Show top opportunities with evidence."},
            {"turn_id": "t-002", "role": "assistant", "content": "Recommend review opportunity and request human review for escalations."},
        ],
    )

