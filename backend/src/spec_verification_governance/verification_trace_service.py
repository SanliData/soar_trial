"""
MODULE: verification_trace_service
PURPOSE: Bounded append-only verification traces (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

_MAX_TRACES = 200
_lock = threading.Lock()
_traces: list[dict[str, Any]] = []

_CANONICAL_EXAMPLES: tuple[dict[str, Any], ...] = (
    {
        "trace_id": "sv_ex_workflow_failure",
        "category": "workflow_failure",
        "detail": "Acceptance validation failed after delegation flap spike.",
    },
    {
        "trace_id": "sv_ex_hallucinated_output",
        "category": "hallucinated_outputs",
        "detail": "Contractor fit claim without citation in procurement draft.",
    },
    {
        "trace_id": "sv_ex_graph_unstable",
        "category": "unstable_graph_reasoning",
        "detail": "Hop variance exceeded rolling threshold during investigation.",
    },
    {
        "trace_id": "sv_ex_retrieval_mismatch",
        "category": "retrieval_mismatch",
        "detail": "Retrieved chunk hash diverged from indexed snapshot.",
    },
    {
        "trace_id": "sv_ex_invalid_orchestration",
        "category": "invalid_orchestration",
        "detail": "Planner proposed capability outside registry allow-list.",
    },
)


def record_verification_trace(category: str, detail: str, trace_id: str | None = None) -> dict[str, Any]:
    tid = trace_id or f"sv_{uuid.uuid4().hex[:14]}"
    ev = {"trace_id": tid, "category": category, "detail": detail, "immutable": True}
    with _lock:
        _traces.append(ev)
        overflow = len(_traces) - _MAX_TRACES
        if overflow > 0:
            del _traces[0:overflow]
    return ev


def export_verification_traces(include_examples: bool = True) -> dict[str, Any]:
    with _lock:
        live = list(_traces)
    examples = list(_CANONICAL_EXAMPLES) if include_examples else []
    return {
        "traces": examples + live,
        "live_count": len(live),
        "example_count": len(examples),
        "buffer_cap": _MAX_TRACES,
    }
