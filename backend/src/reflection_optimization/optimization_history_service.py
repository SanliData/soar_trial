"""
MODULE: optimization_history_service
PURPOSE: Append-only optimization approval history (H-022)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4

from src.reflection_optimization.reflection_schema import OptimizationHistoryEntry

_MAX_HISTORY = 5000
_history: list[OptimizationHistoryEntry] = []


def record_history(
    workflow_name: str,
    previous_candidate_id: str | None,
    accepted_candidate_id: str | None,
    evaluation_notes: str,
    approved_by: str,
) -> OptimizationHistoryEntry:
    entry = OptimizationHistoryEntry(
        history_id=str(uuid4()),
        workflow_name=workflow_name,
        previous_candidate_id=previous_candidate_id,
        accepted_candidate_id=accepted_candidate_id,
        evaluation_notes=evaluation_notes,
        approved_by=approved_by,
        created_at=datetime.utcnow(),
    )
    _history.append(entry)
    overflow = len(_history) - _MAX_HISTORY
    if overflow > 0:
        del _history[0:overflow]
    return entry


def list_history(limit: int = 100) -> List[OptimizationHistoryEntry]:
    if limit < 1:
        limit = 1
    return list(_history[-limit:])


def clear_history_for_tests() -> None:
    _history.clear()
