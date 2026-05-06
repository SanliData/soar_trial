"""
MODULE: evaluation_session_registry
PURPOSE: Deterministic registry for evaluation sessions (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

EVAL_EPOCH = "2026-01-01T00:00:00Z"

***REMOVED*** Bounded in-memory registry (foundation only).
_SESSIONS: Dict[str, Dict[str, Any]] = {}
_ORDER: List[str] = []
_MAX_SESSIONS = 50


def _bounded_put(session_id: str, record: dict[str, Any]) -> None:
    sid = (session_id or "").strip()
    if not sid:
        raise ValueError("session_id required")
    if sid not in _SESSIONS:
        _ORDER.append(sid)
    _SESSIONS[sid] = dict(record)
    while len(_ORDER) > _MAX_SESSIONS:
        old = _ORDER.pop(0)
        _SESSIONS.pop(old, None)


def create_session(*, session_id: str, workflow_scope: str, evaluation_type: str) -> dict[str, Any]:
    sid = (session_id or "").strip()
    wf = (workflow_scope or "").strip() or "procurement_analysis"
    et = (evaluation_type or "").strip() or "operational_compliance"
    record = {
        "session_id": sid,
        "workflow_scope": wf,
        "evaluation_type": et,
        "conversation_length": 0,
        "policy_status": "aligned",
        "approval_events": [],
        "created_at": EVAL_EPOCH,
        "deterministic": True,
    }
    _bounded_put(sid, record)
    return dict(record)


def append_turn(*, session_id: str, turn_id: str, role: str, content: str) -> dict[str, Any]:
    sid = (session_id or "").strip()
    if sid not in _SESSIONS:
        raise ValueError("unknown session")
    rec = dict(_SESSIONS[sid])
    rec["conversation_length"] = int(rec.get("conversation_length") or 0) + 1
    rec.setdefault("turns", [])
    rec["turns"].append({"turn_id": (turn_id or "").strip(), "role": (role or "").strip(), "content": (content or ""), "deterministic": True})
    _bounded_put(sid, rec)
    return dict(rec)


def record_approval_event(*, session_id: str, event: dict[str, Any]) -> dict[str, Any]:
    sid = (session_id or "").strip()
    if sid not in _SESSIONS:
        raise ValueError("unknown session")
    rec = dict(_SESSIONS[sid])
    rec.setdefault("approval_events", [])
    rec["approval_events"].append(dict(event))
    _bounded_put(sid, rec)
    return dict(rec)


def set_policy_status(*, session_id: str, policy_status: str) -> dict[str, Any]:
    sid = (session_id or "").strip()
    if sid not in _SESSIONS:
        raise ValueError("unknown session")
    rec = dict(_SESSIONS[sid])
    rec["policy_status"] = (policy_status or "").strip()
    _bounded_put(sid, rec)
    return dict(rec)


def export_sessions(*, limit: int = 25) -> dict[str, Any]:
    lim = max(1, min(int(limit), 50))
    ids = list(_ORDER)[-lim:]
    rows = [dict(_SESSIONS[sid]) for sid in ids]
    return {"sessions": rows, "session_count": len(rows), "deterministic": True}

