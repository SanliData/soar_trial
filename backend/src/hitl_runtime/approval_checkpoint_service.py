"""
MODULE: approval_checkpoint_service
PURPOSE: Approval checkpoints (explicit metadata, no skipping) (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.hitl_runtime.approval_event_service import record_approval_event
from src.hitl_runtime.human_review_queue import enqueue


def export_checkpoints() -> dict[str, Any]:
    checkpoints = [
        {"checkpoint_id": "cp-procurement-escalation", "trigger": "procurement escalation", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-contractor-onboarding", "trigger": "contractor onboarding", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-workflow-mutation", "trigger": "workflow mutation", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-bulk-export", "trigger": "bulk export", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-graph-rewrite", "trigger": "graph rewrite", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-external-submission", "trigger": "external submission", "approval_required": True, "deterministic": True},
        {"checkpoint_id": "cp-high-risk-recommendation", "trigger": "high-risk recommendation", "approval_required": True, "deterministic": True},
    ]
    return {"checkpoints": checkpoints, "deterministic": True, "no_hidden_approval_skipping": True}


def trigger_checkpoint(*, workflow_id: str, checkpoint_id: str, reason: str, risk_level: str) -> dict[str, Any]:
    """
    Metadata-only foundation: creates an approval-required event and enqueues a human review item.
    """
    wid = (workflow_id or "").strip() or "wf-demo-001"
    cid = (checkpoint_id or "").strip()
    if not cid:
        raise ValueError("checkpoint_id required")
    ev = record_approval_event(workflow_id=wid, checkpoint_id=cid, state="APPROVAL_REQUIRED", reason=reason)
    q = enqueue(queue_id=f"q-{wid}-{cid}", workflow_scope="procurement_analysis", risk_level=risk_level, approval_reason=reason)
    return {"approval_event": ev, "queue_item": q, "deterministic": True, "automatic_approval": False}

