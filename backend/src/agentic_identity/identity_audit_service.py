"""
MODULE: identity_audit_service
PURPOSE: Immutable-style audit metadata for identity usage (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

AUDIT_EPOCH = "2026-01-01T00:00:00Z"

_AUDIT: Dict[str, List[Dict[str, Any]]] = {}
_MAX = 200


def record_identity_event(*, identity_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    iid = (identity_id or "").strip()
    if not iid:
        raise ValueError("identity_id required")
    events = list(_AUDIT.get(iid, []))
    ev = {
        "audit_id": f"{iid}:{len(events)+1:04d}",
        "identity_id": iid,
        "event_type": (event_type or "").strip(),
        "event_timestamp": AUDIT_EPOCH,
        "payload": dict(payload or {}),
        "deterministic": True,
        "immutable_style": True,
    }
    events.append(ev)
    if len(events) > _MAX:
        events = events[-_MAX:]
    _AUDIT[iid] = events
    return ev


def export_identity_audit_log(*, identity_id: str = "id-001", limit: int = 50) -> dict[str, Any]:
    iid = (identity_id or "").strip() or "id-001"
    lim = max(1, min(int(limit), 200))
    events = list(_AUDIT.get(iid, []))[-lim:]
    if not events:
        record_identity_event(identity_id=iid, event_type="IDENTITY_ISSUED", payload={"issued_by": "identity_admin"})
        events = list(_AUDIT.get(iid, []))[-lim:]
    return {"identity_id": iid, "events": events, "deterministic": True}

