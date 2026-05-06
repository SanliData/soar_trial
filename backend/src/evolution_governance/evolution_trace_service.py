"""
MODULE: evolution_trace_service
PURPOSE: Auditable evolution traces — deterministic metadata (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_MAX_TRACES = 200
_LIVE_BUFFER: list[dict[str, Any]] = []

CANONICAL_TRACES: list[dict[str, Any]] = [
    {
        "trace_id": "evo-canonical-001",
        "trace_type": "mutation_proposal",
        "summary": "Workflow optimization proposal recorded; awaiting sandbox.",
        "deterministic": True,
    },
    {
        "trace_id": "evo-canonical-002",
        "trace_type": "sandbox_result",
        "summary": "Sandbox scores computed; no production mutation.",
        "deterministic": True,
    },
    {
        "trace_id": "evo-canonical-003",
        "trace_type": "rollback_event",
        "summary": "Rollback path validated pre-deploy (dry run).",
        "deterministic": True,
    },
    {
        "trace_id": "evo-canonical-004",
        "trace_type": "governance_approval",
        "summary": "Governance gate pending — human approval required for any promotion.",
        "deterministic": True,
    },
]


def append_evolution_trace(entry: dict[str, Any]) -> None:
    """Bounded append-only buffer for optional live instrumentation — foundation hook."""
    _LIVE_BUFFER.append(dict(entry))
    if len(_LIVE_BUFFER) > _MAX_TRACES:
        del _LIVE_BUFFER[: len(_LIVE_BUFFER) - _MAX_TRACES]


def export_evolution_traces() -> dict[str, Any]:
    return {
        "canonical": list(CANONICAL_TRACES),
        "live_buffer_size": len(_LIVE_BUFFER),
        "live_recent": list(_LIVE_BUFFER[-20:]) if _LIVE_BUFFER else [],
        "max_buffer": _MAX_TRACES,
    }
