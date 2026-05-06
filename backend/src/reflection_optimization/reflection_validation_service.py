"""
MODULE: reflection_validation_service
PURPOSE: Guardrails for reflection records and approval transitions (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from src.reflection_optimization.reflection_schema import (
    ApprovalStatusLiteral,
    CreateTraceRequest,
)


def validate_trace_request(body: CreateTraceRequest) -> None:
    wf = (body.workflow_name or "").strip()
    if not wf:
        raise ValueError("workflow_name is required")
    if not body.success and not body.failure_modes:
        raise ValueError("failure_modes must be non-empty when success is false")


def validate_approval_transition(current: ApprovalStatusLiteral, target: ApprovalStatusLiteral) -> None:
    if current != "pending":
        raise ValueError(f"cannot transition from approval_status={current}; only pending candidates change")
    if target not in {"approved", "rejected", "archived"}:
        raise ValueError(f"invalid approval transition target: {target}")
