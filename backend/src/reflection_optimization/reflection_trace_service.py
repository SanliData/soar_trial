"""
MODULE: reflection_trace_service
PURPOSE: In-memory reflection trace storage (H-022 foundation)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from src.reflection_optimization.reflection_schema import CreateTraceRequest, ReflectionTrace

_MAX_TRACES = 2000
_traces: list[ReflectionTrace] = []


def record_trace(payload: CreateTraceRequest) -> ReflectionTrace:
    trace = ReflectionTrace(
        trace_id=str(uuid4()),
        task_type=payload.task_type,
        workflow_name=payload.workflow_name.strip(),
        input_summary=payload.input_summary,
        output_summary=payload.output_summary,
        success=payload.success,
        score=payload.score,
        failure_modes=list(payload.failure_modes),
        execution_notes=payload.execution_notes,
        created_at=datetime.utcnow(),
    )
    _traces.append(trace)
    overflow = len(_traces) - _MAX_TRACES
    if overflow > 0:
        del _traces[0:overflow]
    return trace


def get_trace(trace_id: str) -> Optional[ReflectionTrace]:
    for t in _traces:
        if t.trace_id == trace_id:
            return t
    return None


def list_recent_traces(limit: int = 50) -> list[ReflectionTrace]:
    if limit < 1:
        limit = 1
    return list(_traces[-limit:])


def filter_by_workflow(workflow_name: str, limit: int = 50) -> list[ReflectionTrace]:
    wf = workflow_name.strip().lower()
    matched = [t for t in _traces if t.workflow_name.lower() == wf]
    return matched[-limit:] if limit > 0 else []


def filter_failed_traces(limit: int = 50) -> list[ReflectionTrace]:
    failed = [t for t in _traces if not t.success]
    return failed[-limit:] if limit > 0 else []


def list_traces_filtered(
    limit: int = 50,
    workflow_name: str | None = None,
    failed_only: bool = False,
) -> list[ReflectionTrace]:
    rows = list(_traces)
    if failed_only:
        rows = [t for t in rows if not t.success]
    if workflow_name and workflow_name.strip():
        wf = workflow_name.strip().lower()
        rows = [t for t in rows if t.workflow_name.lower() == wf]
    if limit < 1:
        limit = 1
    return rows[-limit:]


def clear_traces_for_tests() -> None:
    _traces.clear()
