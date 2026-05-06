"""
MODULE: runtime_observability_service
PURPOSE: Auditable reliability traces — append-only bounded buffer (H-033)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

_MAX_TRACE_EVENTS = 200
_lock = threading.Lock()
_trace_events: list[dict[str, Any]] = []

***REMOVED*** Canonical example traces (always included in export for explainability).
_CANONICAL_EXAMPLES: tuple[dict[str, Any], ...] = (
    {
        "trace_id": "rel_ex_retrieval_degradation",
        "category": "retrieval_degradation",
        "severity": "medium",
        "detail": "Elevated duplicate retrieval ratio in session window.",
    },
    {
        "trace_id": "rel_ex_graph_instability",
        "category": "graph_instability",
        "severity": "low",
        "detail": "Graph hop variance exceeded rolling threshold.",
    },
    {
        "trace_id": "rel_ex_workflow_instability",
        "category": "workflow_instability",
        "severity": "medium",
        "detail": "Retry burst detected during delegated workflow.",
    },
    {
        "trace_id": "rel_ex_context_collapse",
        "category": "context_collapse",
        "severity": "high",
        "detail": "Context rot score crossed compression recommendation tier.",
    },
    {
        "trace_id": "rel_ex_prompt_degradation",
        "category": "prompt_degradation",
        "severity": "low",
        "detail": "Prompt hash churn without evaluation suite bump.",
    },
)


def record_trace_event(category: str, severity: str, detail: str, trace_id: str | None = None) -> dict[str, Any]:
    tid = trace_id or f"rel_{uuid.uuid4().hex[:12]}"
    ev = {"trace_id": tid, "category": category, "severity": severity, "detail": detail}
    with _lock:
        _trace_events.append(ev)
        overflow = len(_trace_events) - _MAX_TRACE_EVENTS
        if overflow > 0:
            del _trace_events[0:overflow]
    return ev


def export_observability_traces(include_examples: bool = True) -> dict[str, Any]:
    with _lock:
        live = list(_trace_events)
    examples = list(_CANONICAL_EXAMPLES) if include_examples else []
    combined = examples + live
    return {
        "traces": combined,
        "live_event_count": len(live),
        "canonical_examples_count": len(examples),
        "buffer_cap": _MAX_TRACE_EVENTS,
        "immutability_note": "client_should_treat_trace_objects_as_read_only",
    }
