"""
MODULE: command_audit_service
PURPOSE: Command audit metadata storage (bounded, deterministic) (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from src.natural_language_control_plane.nl_control_validation_service import validate_command_audit_record

_MAX_AUDITS = 200
_AUDITS: list[dict[str, Any]] = []


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_command_audit(
    *,
    raw_command_summary: str,
    parsed_intent: str,
    routed_workflow: str,
    approval_required: bool,
    decision_status: str = "pending",
) -> dict[str, Any]:
    payload = {
        "raw_command_summary": (raw_command_summary or "").strip()[:240],
        "parsed_intent": (parsed_intent or "").strip(),
        "routed_workflow": (routed_workflow or "").strip(),
        "approval_required": bool(approval_required),
        "decision_status": (decision_status or "pending").strip(),
        "created_at": _now_iso(),
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    rec = {"command_id": f"cmd-{digest}", **payload}
    validate_command_audit_record(rec)
    _AUDITS.append(dict(rec))
    if len(_AUDITS) > _MAX_AUDITS:
        del _AUDITS[: len(_AUDITS) - _MAX_AUDITS]
    return dict(rec)


def export_audit_log(*, limit: int = 30) -> dict[str, Any]:
    lim = max(1, min(int(limit), 200))
    return {
        "audits": list(_AUDITS[-lim:]),
        "max_buffer": _MAX_AUDITS,
        "audit_required": True,
        "deterministic": True,
    }

