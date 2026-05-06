"""
MODULE: skill_execution_trace_service
PURPOSE: Auditable skill runtime traces — bounded buffer (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_MAX_TRACES = 200
_LIVE_BUFFER: list[dict[str, Any]] = []

CANONICAL_TRACES: list[dict[str, Any]] = [
    {
        "trace_id": "sk-trace-001",
        "trace_type": "activation",
        "summary": "graph_investigator activation via explicit_command (dry-run manifest).",
        "immutable_preferred": True,
    },
    {
        "trace_id": "sk-trace-002",
        "trace_type": "blocked_permission",
        "summary": "browser_compliance blocked — principal_skill_grant=false.",
        "immutable_preferred": True,
    },
    {
        "trace_id": "sk-trace-003",
        "trace_type": "dependency_load",
        "summary": "reliability_audit loaded ahead of graph_investigator dependency closure.",
        "immutable_preferred": True,
    },
    {
        "trace_id": "sk-trace-004",
        "trace_type": "execution_failure",
        "summary": "Scoped load denied — runtime_scope mismatch (synthetic).",
        "immutable_preferred": True,
    },
    {
        "trace_id": "sk-trace-005",
        "trace_type": "escalation",
        "summary": "Escalation policy human_above_threshold_spend triggered (manifest only).",
        "immutable_preferred": True,
    },
]


def append_skill_trace(entry: dict[str, Any]) -> None:
    _LIVE_BUFFER.append(dict(entry))
    if len(_LIVE_BUFFER) > _MAX_TRACES:
        del _LIVE_BUFFER[: len(_LIVE_BUFFER) - _MAX_TRACES]


def export_skill_execution_traces() -> dict[str, Any]:
    return {
        "canonical": list(CANONICAL_TRACES),
        "live_buffer_size": len(_LIVE_BUFFER),
        "live_recent": list(_LIVE_BUFFER[-20:]) if _LIVE_BUFFER else [],
        "max_buffer": _MAX_TRACES,
        "auditable": True,
    }
