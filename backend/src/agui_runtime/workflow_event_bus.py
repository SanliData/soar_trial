"""
MODULE: workflow_event_bus
PURPOSE: Deterministic workflow event propagation (metadata only) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

BUS_EPOCH = "2026-01-01T00:00:00Z"

_BUS: Dict[str, List[Dict[str, Any]]] = {}
_MAX_EVENTS = 200


def publish_event(*, workflow_id: str, event_type: str, source_service: str, risk_level: str = "low") -> dict[str, Any]:
    wid = (workflow_id or "").strip() or "wf-demo-001"
    events = list(_BUS.get(wid, []))
    seq = len(events) + 1
    ev = {
        "workflow_id": wid,
        "event_sequence": int(seq),
        "event_type": (event_type or "").strip(),
        "event_timestamp": BUS_EPOCH,
        "source_service": (source_service or "").strip(),
        "risk_level": (risk_level or "").strip() or "low",
        "metadata_only": True,
        "deterministic": True,
    }
    events.append(ev)
    if len(events) > _MAX_EVENTS:
        events = events[-_MAX_EVENTS :]
    _BUS[wid] = events
    return ev


def export_workflow_bus(*, workflow_id: str = "wf-demo-001", limit: int = 80) -> dict[str, Any]:
    wid = (workflow_id or "").strip() or "wf-demo-001"
    lim = max(1, min(int(limit), 200))
    events = list(_BUS.get(wid, []))[-lim:]
    return {"workflow_id": wid, "events": events, "event_count": len(events), "deterministic": True}

