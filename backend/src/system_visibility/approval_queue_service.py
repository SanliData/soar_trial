"""
MODULE: approval_queue_service
PURPOSE: Approval queue visibility (metadata only; no auto-approval) (H-046)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.natural_language_control_plane.command_audit_service import export_audit_log


def export_approval_queue() -> dict[str, Any]:
    audits = export_audit_log(limit=80).get("audits") or []
    pending = [a for a in audits if a.get("approval_required") is True and a.get("decision_status") == "pending"]
    denied = [a for a in audits if a.get("decision_status") == "denied"]
    escalated = [a for a in audits if a.get("decision_status") == "escalated"]
    return {
        "pending_approvals": pending,
        "escalated_operations": escalated,
        "denied_operations": denied,
        "unresolved_governance_events": len(pending) + len(escalated),
        "automatic_approval": False,
        "deterministic": True,
    }

