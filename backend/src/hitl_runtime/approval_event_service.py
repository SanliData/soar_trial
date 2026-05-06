"""
MODULE: approval_event_service
PURPOSE: Approval event records (metadata only) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from src.hitl_runtime.approval_validation_service import reject_auto_approval, require_approval_lineage

APPROVAL_EPOCH = "2026-01-01T00:00:00Z"

_EVENTS: Dict[str, Dict[str, Any]] = {}


def record_approval_event(*, workflow_id: str, checkpoint_id: str, state: str, reason: str) -> dict[str, Any]:
    wid = (workflow_id or "").strip()
    cid = (checkpoint_id or "").strip()
    st = (state or "").strip()
    if not wid or not cid or not st:
        raise ValueError("workflow_id/checkpoint_id/state required")
    ev = {
        "approval_event_id": f"{wid}:{cid}:{st}",
        "state": st,
        "reason": (reason or "").strip(),
        "approval_lineage": {"workflow_id": wid, "checkpoint_id": cid},
        "timestamp": APPROVAL_EPOCH,
        "automatic_approval": False,
        "deterministic": True,
    }
    require_approval_lineage(ev)
    reject_auto_approval(ev)
    _EVENTS[ev["approval_event_id"]] = ev
    return ev


def export_approval_events(*, limit: int = 50) -> dict[str, Any]:
    lim = max(1, min(int(limit), 200))
    keys = sorted(_EVENTS.keys())
    rows = [_EVENTS[k] for k in keys[-lim:]]
    return {"approval_events": rows, "deterministic": True}

