"""
MODULE: human_approval_stream
PURPOSE: Approval stream metadata for AG-UI timelines (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.system_visibility.approval_queue_service import export_approval_queue


def export_approval_stream() -> dict[str, Any]:
    q = export_approval_queue()
    pending = q.get("pending_approvals") or []
    events = []
    for idx, p in enumerate(pending[:5], start=1):
        events.append(
            {
                "approval_event_id": f"appr-{idx:03d}",
                "state": "APPROVAL_REQUIRED",
                "reason": p.get("approval_reason") or "human approval required",
                "target": p.get("target") or "unknown",
                "escalation_required": bool(p.get("escalation_required")),
                "timeout_warning": False,
                "deterministic": True,
            }
        )
    return {"approval_stream": events, "deterministic": True, "audit_required": True}

