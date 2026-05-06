"""
CORE: upap/audit
PURPOSE: Emit audit events for every gate outcome.
ENCODING: UTF-8 WITHOUT BOM

Events: upap_gate_pass, upap_gate_fail
Payload: trace_id, run_id, query_id, gate_name, status, reason, limits, timestamp.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def emit_upap_gate_event(
    event_type: str,
    gate_name: str,
    trace_id: str,
    run_id: str,
    query_id: str,
    status: str,
    reason: Optional[str] = None,
    limits: Optional[Dict[str, Any]] = None,
    timestamp: Optional[str] = None,
) -> None:
    """
    Emit audit event. event_type in ("upap_gate_pass", "upap_gate_fail").
    Payload MUST include trace_id, run_id, query_id, gate_name, status, reason, limits, timestamp.
    """
    ts = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "event": event_type,
        "trace_id": trace_id,
        "run_id": run_id,
        "query_id": query_id,
        "gate_name": gate_name,
        "status": status,
        "reason": reason,
        "limits": limits or {},
        "timestamp": ts,
    }
    logger.info("UPAP audit %s %s %s", event_type, gate_name, status, extra={"upap_audit": payload})
