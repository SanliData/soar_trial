"""
ROUTER: conversational_evaluation_router
PURPOSE: Conversational evaluation runtime facade (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.conversational_evaluation.evaluation_session_registry import export_sessions
from src.conversational_evaluation.multi_turn_trace_service import export_traces
from src.conversational_evaluation.policy_alignment_service import export_policy_alignment
from src.conversational_evaluation.turn_level_analysis_service import export_turn_level_analysis

router = APIRouter(prefix="/system/conversation-eval", tags=["conversation-eval"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "conversational_evaluation_foundation": True,
        "deterministic": True,
        "autonomous_workflow_completion": False,
        "hidden_evaluation_weighting": False,
    }
    out.update(payload)
    return out


@router.get("/sessions")
async def get_sessions() -> Dict[str, Any]:
    return _envelope(export_sessions(limit=25))


@router.get("/traces")
async def get_traces() -> Dict[str, Any]:
    ***REMOVED*** Demo session trace for foundation.
    return _envelope(export_traces(session_id="sess-demo-001", limit=80))


@router.get("/policy-alignment")
async def get_policy_alignment() -> Dict[str, Any]:
    return _envelope(export_policy_alignment())


@router.get("/turn-analysis")
async def get_turn_analysis() -> Dict[str, Any]:
    return _envelope(export_turn_level_analysis())


