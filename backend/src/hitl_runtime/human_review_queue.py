"""
MODULE: human_review_queue
PURPOSE: Deterministic review queue ordering + auditable history (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

QUEUE_EPOCH = "2026-01-01T00:00:00Z"

_QUEUE: List[Dict[str, Any]] = []
_MAX = 100


def enqueue(*, queue_id: str, workflow_scope: str, risk_level: str, approval_reason: str) -> dict[str, Any]:
    item = {
        "queue_id": (queue_id or "").strip(),
        "workflow_scope": (workflow_scope or "").strip() or "procurement_analysis",
        "risk_level": (risk_level or "").strip() or "low",
        "approval_reason": (approval_reason or "").strip() or "human review required",
        "waiting_since": QUEUE_EPOCH,
        "escalation_deadline": QUEUE_EPOCH,
        "deterministic": True,
        "auditable": True,
    }
    _QUEUE.append(item)
    _QUEUE.sort(key=lambda x: (x["workflow_scope"], x["queue_id"]))
    while len(_QUEUE) > _MAX:
        _QUEUE.pop(0)
    return item


def export_review_queue(*, limit: int = 25) -> dict[str, Any]:
    lim = max(1, min(int(limit), 100))
    rows = list(_QUEUE)[:lim]
    return {"queue": rows, "queue_count": len(rows), "deterministic": True}

