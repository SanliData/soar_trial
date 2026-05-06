"""
MODULE: context_lifecycle_service
PURPOSE: Context lifecycle registry (register/list/prioritize/stale/summarize) (H-044)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

from src.context_compression.semantic_context_summarizer import summarize_context_collection
from src.context_orchestration.context_validation_service import validate_context_item

_STORE: dict[str, dict[str, Any]] = {}
_STALE: set[str] = set()


def reset_context_registry_for_tests() -> None:
    _STORE.clear()
    _STALE.clear()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def register_context(item: dict[str, Any]) -> dict[str, Any]:
    """
    Register (or update) a context item by context_id.

    Rules:
    - validation is strict
    - no hidden deletion
    - overwrites are explicit and auditable by caller because the full item is stored
    """
    validate_context_item(item)
    cid = str(item["context_id"]).strip()
    stored = dict(item)
    stored["registered_at"] = _now_iso()
    _STORE[cid] = stored
    return dict(stored)


def list_context(*, workflow_scope: str | None = None, include_stale: bool = True) -> list[dict[str, Any]]:
    rows = []
    wf = workflow_scope.strip() if isinstance(workflow_scope, str) and workflow_scope.strip() else None
    for cid in sorted(_STORE.keys()):
        row = dict(_STORE[cid])
        row["is_stale"] = cid in _STALE
        if wf and row.get("workflow_scope") != wf:
            continue
        if not include_stale and row["is_stale"]:
            continue
        rows.append(row)
    return rows


def mark_context_stale(context_id: str, *, reason: str = "stale") -> dict[str, Any]:
    cid = (context_id or "").strip()
    if cid not in _STORE:
        raise ValueError("unknown context_id")
    _STALE.add(cid)
    row = dict(_STORE[cid])
    row["is_stale"] = True
    row["stale_reason"] = (reason or "stale").strip()[:200]
    row["stale_marked_at"] = _now_iso()
    _STORE[cid] = dict(row)
    return row


def _priority_key(item: dict[str, Any]) -> tuple[int, int, str]:
    """
    Deterministic prioritization:
    - higher priority first
    - non-stale preferred
    - tie-break by context_id
    """
    cid = str(item.get("context_id") or "").strip()
    pr = int(item.get("priority") or 0)
    stale_penalty = 1 if cid in _STALE else 0
    return (-pr, stale_penalty, cid)


def prioritize_context(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = [dict(x) for x in items]
    for it in normalized:
        validate_context_item(it)
    normalized.sort(key=_priority_key)
    return normalized


def summarize_context_set(
    items: list[dict[str, Any]],
    *,
    max_tokens_total: int = 8000,
    allow_guardrail_compression: bool = False,
) -> dict[str, Any]:
    """
    Deterministic summarization over a set while respecting guardrail visibility.
    """
    for it in items:
        validate_context_item(it)
    return summarize_context_collection(
        items,
        max_tokens_total=max_tokens_total,
        allow_guardrail_compression=allow_guardrail_compression,
    )

