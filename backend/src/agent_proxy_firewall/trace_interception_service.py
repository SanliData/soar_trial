"""
MODULE: trace_interception_service
PURPOSE: Auditable interception traces — bounded buffer (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_MAX_TRACES = 200
_LIVE_BUFFER: list[dict[str, Any]] = []

CANONICAL_TRACES: list[dict[str, Any]] = [
    {
        "trace_id": "fw-canonical-001",
        "trace_type": "blocked_prompt",
        "summary": "Synthetic injection marker blocked at prompt_injection_scan.",
        "immutable_preferred": True,
    },
    {
        "trace_id": "fw-canonical-002",
        "trace_type": "blocked_output",
        "summary": "Destructive command fragment blocked at destructive_command_scan.",
        "immutable_preferred": True,
    },
    {
        "trace_id": "fw-canonical-003",
        "trace_type": "execution_denial",
        "summary": "External submit denied — signed payload missing (dry run).",
        "immutable_preferred": True,
    },
    {
        "trace_id": "fw-canonical-004",
        "trace_type": "firewall_escalation",
        "summary": "Browser action scan escalated unscoped navigation hint.",
        "immutable_preferred": True,
    },
    {
        "trace_id": "fw-canonical-005",
        "trace_type": "policy_violation",
        "summary": "Policy domain graph_mutation_policy blocked unscoped write directive.",
        "immutable_preferred": True,
    },
]


def append_interception_trace(entry: dict[str, Any]) -> None:
    _LIVE_BUFFER.append(dict(entry))
    if len(_LIVE_BUFFER) > _MAX_TRACES:
        del _LIVE_BUFFER[: len(_LIVE_BUFFER) - _MAX_TRACES]


def export_interception_traces() -> dict[str, Any]:
    return {
        "canonical": list(CANONICAL_TRACES),
        "live_buffer_size": len(_LIVE_BUFFER),
        "live_recent": list(_LIVE_BUFFER[-20:]) if _LIVE_BUFFER else [],
        "max_buffer": _MAX_TRACES,
        "auditable": True,
    }
