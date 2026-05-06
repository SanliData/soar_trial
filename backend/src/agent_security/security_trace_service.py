"""
MODULE: security_trace_service
PURPOSE: Append-only security event traces for audit (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from threading import Lock
from typing import Any


class SecurityTraceStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._rows: list[dict[str, Any]] = []

    def append(self, event_type: str, detail: dict[str, Any]) -> dict[str, Any]:
        row = {
            "trace_id": f"sec_{uuid.uuid4().hex[:16]}",
            "event_type": event_type,
            "detail": dict(detail),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._rows.append(row)
        return row

    def list_traces(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._rows)

    def clear(self) -> None:
        with self._lock:
            self._rows.clear()


_store = SecurityTraceStore()


def get_security_trace_store() -> SecurityTraceStore:
    return _store


def reset_security_trace_store_for_tests() -> None:
    _store.clear()
