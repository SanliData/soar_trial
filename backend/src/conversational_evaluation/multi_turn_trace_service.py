"""
MODULE: multi_turn_trace_service
PURPOSE: Multi-turn immutable-style trace metadata (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

TRACE_EPOCH = "2026-01-01T00:00:00Z"

_TRACE: Dict[str, List[Dict[str, Any]]] = {}
_MAX_EVENTS_PER_SESSION = 200


def append_trace_event(*, session_id: str, event_type: str, source_service: str, payload: dict[str, Any]) -> dict[str, Any]:
    sid = (session_id or "").strip()
    if not sid:
        raise ValueError("session_id required")
    row = {
        "event_id": f"{sid}:{len(_TRACE.get(sid, [])) + 1:04d}",
        "event_type": (event_type or "").strip(),
        "event_timestamp": TRACE_EPOCH,
        "source_service": (source_service or "").strip(),
        "payload": dict(payload or {}),
        "deterministic": True,
    }
    events = list(_TRACE.get(sid, []))
    events.append(row)
    if len(events) > _MAX_EVENTS_PER_SESSION:
        events = events[-_MAX_EVENTS_PER_SESSION :]
    _TRACE[sid] = events
    return row


def export_traces(*, session_id: str, limit: int = 80) -> dict[str, Any]:
    sid = (session_id or "").strip()
    lim = max(1, min(int(limit), 200))
    events = list(_TRACE.get(sid, []))[-lim:]
    return {"session_id": sid, "events": events, "event_count": len(events), "deterministic": True}

