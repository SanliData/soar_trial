"""
ROUTER: agent_security_router
PURPOSE: HTTP facade for trust registry and sanitization (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.agent_security.agent_risk_scoring_service import compute_risk_score
from src.agent_security.prompt_sanitization_service import sanitize_prompt
from src.agent_security.retrieval_sanitization_service import sanitize_retrieval
from src.agent_security.security_trace_service import get_security_trace_store
from src.agent_security.security_validation_service import (
    RiskScoreRequest,
    SanitizePromptRequest,
    SanitizeRetrievalRequest,
)
from src.agent_security.tool_capability_registry import export_capabilities_manifest

router = APIRouter(prefix="/system/security", tags=["agent-security"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "agent_security_foundation": True,
        "autonomous_tool_execution": False,
        "unrestricted_mcp_execution": False,
    }
    out.update(payload)
    return out


@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    return _envelope(export_capabilities_manifest())


@router.post("/sanitize-prompt")
async def post_sanitize_prompt(body: SanitizePromptRequest) -> Dict[str, Any]:
    result = sanitize_prompt(body.text)
    trace = get_security_trace_store().append(
        "prompt_sanitized",
        {"findings_count": len(result.get("findings") or []), "modified": result.get("modified")},
    )
    return _envelope({"sanitization": result, "trace": trace})


@router.post("/sanitize-retrieval")
async def post_sanitize_retrieval(body: SanitizeRetrievalRequest) -> Dict[str, Any]:
    result = sanitize_retrieval(body.content, body.content_type)
    trace = get_security_trace_store().append(
        "retrieval_sanitized",
        {"findings_count": len(result.get("findings") or []), "modified": result.get("modified")},
    )
    return _envelope({"sanitization": result, "trace": trace})


@router.get("/traces")
async def get_traces() -> Dict[str, Any]:
    rows = get_security_trace_store().list_traces()
    return _envelope({"traces": rows})


@router.post("/risk-score")
async def post_risk_score(body: RiskScoreRequest) -> Dict[str, Any]:
    result = compute_risk_score(body.prompt_text, body.retrieval_sample, body.requested_tools)
    trace = get_security_trace_store().append(
        "risk_scored",
        {"risk_score": result.get("risk_score")},
    )
    return _envelope({"risk": result, "trace": trace})
