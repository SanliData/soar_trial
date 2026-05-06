"""
AGENTS: execution_trace
PURPOSE: Record skill calls, tool outputs, decision steps; store in Redis for debug
"""
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REDIS_KEY_PREFIX = "agents:trace"
REDIS_TTL = 86400 * 2  ***REMOVED*** 2 days


def _redis():
    try:
        from src.core.cache import get_redis_client
        return get_redis_client()
    except Exception:
        return None


def create_trace(session_id: Optional[str] = None) -> str:
    """Create a new trace, return trace_id."""
    trace_id = f"trace_{uuid.uuid4().hex[:16]}"
    r = _redis()
    if not r:
        return trace_id
    try:
        payload = {
            "trace_id": trace_id,
            "session_id": session_id,
            "started_at": time.time(),
            "skill_calls": [],
            "tool_outputs": [],
            "decision_steps": [],
        }
        r.setex(f"{REDIS_KEY_PREFIX}:{trace_id}", REDIS_TTL, json.dumps(payload))
    except Exception as e:
        logger.debug("create_trace: %s", e)
    return trace_id


def _get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    r = _redis()
    if not r:
        return None
    try:
        raw = r.get(f"{REDIS_KEY_PREFIX}:{trace_id}")
        if not raw:
            return None
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception:
        return None


def _save_trace(trace_id: str, payload: Dict[str, Any]) -> bool:
    r = _redis()
    if not r:
        return False
    try:
        r.setex(f"{REDIS_KEY_PREFIX}:{trace_id}", REDIS_TTL, json.dumps(payload))
        return True
    except Exception as e:
        logger.debug("_save_trace: %s", e)
        return False


def append_skill_call(trace_id: str, skill_name: str, inputs: Dict[str, Any], output_summary: Optional[Dict[str, Any]] = None, duration_ms: Optional[int] = None) -> None:
    """Append a skill call to the trace."""
    t = _get_trace(trace_id)
    if not t:
        return
    t.setdefault("skill_calls", []).append({
        "skill_name": skill_name,
        "inputs": inputs,
        "output_summary": output_summary or {},
        "duration_ms": duration_ms,
    })
    _save_trace(trace_id, t)


def append_tool_output(trace_id: str, tool_name: str, output: Any, success: bool = True) -> None:
    """Append a tool output to the trace."""
    t = _get_trace(trace_id)
    if not t:
        return
    t.setdefault("tool_outputs", []).append({
        "tool_name": tool_name,
        "output": output if not isinstance(output, (dict, list, str)) or len(str(output)) < 2000 else str(output)[:2000],
        "success": success,
    })
    _save_trace(trace_id, t)


def append_decision_step(trace_id: str, step: str, reason: str, payload: Optional[Dict[str, Any]] = None) -> None:
    """Append a decision step (e.g. intent, chosen skill sequence) to the trace."""
    t = _get_trace(trace_id)
    if not t:
        return
    t.setdefault("decision_steps", []).append({
        "step": step,
        "reason": reason,
        "payload": payload or {},
    })
    _save_trace(trace_id, t)


def get_trace(trace_id: str) -> Optional[Dict[str, Any]]:
    """Return full trace by id (for GET /agents/trace/{trace_id})."""
    return _get_trace(trace_id)


def finish_trace(trace_id: str, final_context_summary: Optional[Dict[str, Any]] = None) -> None:
    """Mark trace as finished and optionally attach final context summary."""
    t = _get_trace(trace_id)
    if not t:
        return
    t["finished_at"] = time.time()
    if final_context_summary is not None:
        t["final_context_summary"] = final_context_summary
    _save_trace(trace_id, t)
