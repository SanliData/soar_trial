"""
MODULE: workflow_session_service
PURPOSE: Workflow session lifecycle — in-memory foundation store (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

from src.workflow_governance.adaptive_effort_service import export_effort_manifest, resolve_effort
from src.workflow_governance.context_decay_service import detect_context_rot
from src.workflow_governance.delegation_policy_service import describe_delegation_policies
from src.workflow_governance.subagent_parallelization_service import describe_parallel_policies
from src.workflow_governance.workflow_contract_registry import WORKFLOW_CONTRACTS, export_contracts_manifest

_lock = threading.Lock()
_sessions: dict[str, dict[str, Any]] = {}


def create_session(workflow_name: str, label: str | None = None) -> dict[str, Any]:
    if workflow_name not in WORKFLOW_CONTRACTS:
        raise ValueError(f"invalid workflow_name: {workflow_name}")
    sid = f"wfs_{uuid.uuid4().hex[:16]}"
    effort = resolve_effort("workflow", workflow_name=workflow_name)
    rec: dict[str, Any] = {
        "session_id": sid,
        "workflow_name": workflow_name,
        "label": (label or "").strip() or None,
        "status": "active",
        "checkpoint_count": 0,
        "turn_count": 0,
        "token_estimate": 0,
        "effort": effort["effort_level"],
    }
    with _lock:
        _sessions[sid] = rec
    return {"session": rec, "created": True}


def summarize_session(session_id: str) -> dict[str, Any]:
    with _lock:
        s = _sessions.get(session_id)
    if not s:
        raise ValueError("session not found")
    rot = detect_context_rot(
        token_estimate=int(s.get("token_estimate") or 0),
        turn_count=int(s.get("turn_count") or 0),
        workflow_name=str(s.get("workflow_name") or ""),
    )
    # Deterministic summary fields derived only from stored session state.
    out = {
        "session_id": s["session_id"],
        "workflow_name": s["workflow_name"],
        "status": s["status"],
        "checkpoint_count": s["checkpoint_count"],
        "effort": s["effort"],
        "context_health": rot["rot_score"],
        "summary_rule": "deterministic_session_snapshot_v1",
    }
    return out


def checkpoint_session(session_id: str) -> dict[str, Any]:
    with _lock:
        s = _sessions.get(session_id)
        if not s:
            raise ValueError("session not found")
        s["checkpoint_count"] = int(s.get("checkpoint_count") or 0) + 1
        cp = s["checkpoint_count"]
        st = s["status"]
    return {"session_id": session_id, "checkpoint_index": cp, "status": st}


def close_session(session_id: str) -> dict[str, Any]:
    with _lock:
        s = _sessions.get(session_id)
        if not s:
            raise ValueError("session not found")
        s["status"] = "closed"
    return {"session_id": session_id, "status": "closed"}


def session_touch(session_id: str, token_estimate: int, turn_increment: int = 1) -> None:
    with _lock:
        s = _sessions.get(session_id)
        if not s:
            raise ValueError("session not found")
        s["token_estimate"] = int(s.get("token_estimate") or 0) + int(token_estimate)
        s["turn_count"] = int(s.get("turn_count") or 0) + int(turn_increment)


def get_governance_runtime_summary() -> dict[str, Any]:
    with _lock:
        active = sum(1 for v in _sessions.values() if v.get("status") == "active")
        total = len(_sessions)
    return {
        "contracts": export_contracts_manifest()["contract_count"],
        "effort_levels": export_effort_manifest()["levels"],
        "delegation": describe_delegation_policies(),
        "parallelization": describe_parallel_policies(),
        "sessions": {"active_count": active, "total_tracked": total},
        "governance_envelope": {
            "unrestricted_autonomous_execution": False,
            "recursive_workflow_swarm": False,
            "self_expanding_workflow_graph": False,
        },
    }
