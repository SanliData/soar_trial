"""
MODULE: prompt_candidate_registry
PURPOSE: Human-review-only prompt candidate registry (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import List, Optional

from src.reflection_optimization.optimization_history_service import record_history
from src.reflection_optimization.prompt_revision_service import build_candidate_from_trace
from src.reflection_optimization.reflection_schema import PromptCandidate
from src.reflection_optimization.reflection_trace_service import get_trace
from src.reflection_optimization.reflection_validation_service import validate_approval_transition

_candidates: dict[str, PromptCandidate] = {}
_MAX_LIST = 1000


def create_candidate_from_trace_id(trace_id: str, workflow_override: Optional[str] = None) -> PromptCandidate:
    trace = get_trace(trace_id)
    if trace is None:
        raise ValueError(f"unknown trace_id: {trace_id}")
    cand = build_candidate_from_trace(trace)
    if workflow_override:
        cand = cand.model_copy(update={"workflow_name": workflow_override.strip()})
    _candidates[cand.candidate_id] = cand
    return cand


def get_candidate(candidate_id: str) -> Optional[PromptCandidate]:
    return _candidates.get(candidate_id)


def list_candidates(limit: int = 50, workflow_name: Optional[str] = None) -> List[PromptCandidate]:
    rows = list(_candidates.values())
    if workflow_name:
        w = workflow_name.strip().lower()
        rows = [c for c in rows if c.workflow_name.lower() == w]
    rows.sort(key=lambda c: c.created_at)
    if limit < 1:
        limit = 1
    return rows[-limit:]


def approve_candidate(candidate_id: str, approved_by: str, evaluation_notes: str = "") -> PromptCandidate:
    cur = _candidates.get(candidate_id)
    if cur is None:
        raise ValueError("unknown candidate_id")
    validate_approval_transition(cur.approval_status, "approved")
    updated = cur.model_copy(
        update={"approval_status": "approved"},
    )
    _candidates[candidate_id] = updated
    record_history(
        workflow_name=updated.workflow_name,
        previous_candidate_id=None,
        accepted_candidate_id=candidate_id,
        evaluation_notes=evaluation_notes or "approved via explicit human action",
        approved_by=approved_by,
    )
    return updated


def reject_candidate(candidate_id: str, rejected_by: str, evaluation_notes: str = "") -> PromptCandidate:
    cur = _candidates.get(candidate_id)
    if cur is None:
        raise ValueError("unknown candidate_id")
    validate_approval_transition(cur.approval_status, "rejected")
    updated = cur.model_copy(update={"approval_status": "rejected"})
    _candidates[candidate_id] = updated
    record_history(
        workflow_name=updated.workflow_name,
        previous_candidate_id=None,
        accepted_candidate_id=None,
        evaluation_notes=evaluation_notes or f"rejected by {rejected_by}",
        approved_by=rejected_by,
    )
    return updated


def clear_candidates_for_tests() -> None:
    _candidates.clear()
