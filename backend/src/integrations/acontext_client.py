"""
INTEGRATION: Acontext client
PURPOSE: Async client wrapper for Acontext external context + observability backend.
ENCODING: UTF-8 WITHOUT BOM

Session schema:
  tenant_id, workspace_id, lead_id, pipeline_stage, trace_id, run_id

DO NOT replace existing DB logic. Acontext is observability + replay layer only.
"""

import asyncio
import hashlib
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)

PipelineStage = Literal["INGEST", "ENRICH", "EXPORT"]

***REMOVED*** In-memory store for observability events (fallback when Acontext API not configured)
_acontext_store: Dict[str, List[Dict[str, Any]]] = {}
_store_lock = asyncio.Lock()


def _is_configured() -> bool:
    """Check if Acontext is configured via env."""
    return bool(os.getenv("ACONTEXT_API_KEY"))


def _get_api_base() -> str:
    """Get Acontext API base URL from env."""
    return os.getenv("ACONTEXT_API_URL", "https://api.acontext.ai/v1").rstrip("/")


async def create_session(
    tenant_id: str,
    workspace_id: str,
    lead_id: Optional[str] = None,
    pipeline_stage: PipelineStage = "INGEST",
    trace_id: str = "",
    run_id: str = "",
) -> str:
    """
    Create an Acontext session.
    Returns session_id.
    """
    session_id = f"{trace_id}:{run_id}" if trace_id and run_id else f"session-{datetime.now(timezone.utc).timestamp()}"
    session = {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "lead_id": lead_id,
        "pipeline_stage": pipeline_stage,
        "trace_id": trace_id,
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if _is_configured():
        try:
            ***REMOVED*** Placeholder: call Acontext API when available
            ***REMOVED*** import httpx
            ***REMOVED*** async with httpx.AsyncClient() as client:
            ***REMOVED***     r = await client.post(f"{_get_api_base()}/sessions", json=session, ...)
            pass
        except Exception as e:
            logger.warning("Acontext create_session failed (fallback to store): %s", e)

    async with _store_lock:
        _acontext_store.setdefault(session_id, [])
        _acontext_store[session_id].append({"type": "SESSION_CREATE", "payload": session})
    return session_id


async def store_message(
    session_id: str,
    role: str,
    content: str | Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Store a message in the session."""
    msg = {
        "role": role,
        "content": content,
        "metadata": metadata or {},
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if _is_configured():
        try:
            ***REMOVED*** Placeholder: call Acontext API
            pass
        except Exception as e:
            logger.warning("Acontext store_message failed: %s", e)

    async with _store_lock:
        _acontext_store.setdefault(session_id, []).append({"type": "MESSAGE", "payload": msg})


async def get_messages(
    session_id: str,
    tenant_id: str,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get messages for a session.
    Tenant isolation: validated before returning. Reject if session.tenant_id != request.tenant_id.
    """
    from src.security.context_guard import ContextGuardError, validate_tenant_access

    async with _store_lock:
        events = _acontext_store.get(session_id, [])
    ***REMOVED*** First event may have tenant_id; validate
    session_tenant = None
    for ev in events:
        p = ev.get("payload", {})
        session_tenant = p.get("tenant_id") or session_tenant
        if session_tenant:
            break
    validate_tenant_access(session_tenant, tenant_id, session_id)
    messages = [e["payload"] for e in events if e.get("type") == "MESSAGE"]
    return messages[-limit:]


async def store_artifact(
    session_id: str,
    tenant_id: str,
    artifact_type: Literal["CSV", "JSON", "PDF"],
    artifact_id: str,
    hash_sha256: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Store artifact metadata (hash only, no raw sensitive values)."""
    enc_key = os.getenv("ACONTEXT_ENCRYPTION_KEY")
    if enc_key:
        ***REMOVED*** AES encrypt hash before storing (simplified: use env key for deterministic encryption)
        hash_sha256 = hashlib.sha256((hash_sha256 + enc_key[:16]).encode()).hexdigest()

    artifact = {
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "hash_sha256": hash_sha256,
        "metadata": metadata or {},
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if _is_configured():
        try:
            ***REMOVED*** Placeholder: call Acontext API
            pass
        except Exception as e:
            logger.warning("Acontext store_artifact failed: %s", e)

    async with _store_lock:
        _acontext_store.setdefault(session_id, []).append({"type": "ARTIFACT", "payload": artifact})


async def store_event(
    session_id: str,
    tenant_id: str,
    event_type: str,
    payload: Dict[str, Any],
    lead_id: Optional[str] = None,
) -> None:
    """Store an observability event. tenant_id stored for replay isolation."""
    event = {
        "event_type": event_type,
        "payload": payload,
        "tenant_id": tenant_id,
        "lead_id": lead_id,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if _is_configured():
        try:
            ***REMOVED*** Placeholder: call Acontext API
            pass
        except Exception as e:
            logger.warning("Acontext store_event failed: %s", e)

    async with _store_lock:
        _acontext_store.setdefault(session_id, []).append({"type": "EVENT", "payload": event})


async def get_events_for_replay(trace_id: str, tenant_id: str) -> List[Dict[str, Any]]:
    """
    Get full ordered event timeline for replay.
    Returns gate decisions, tool calls, artifacts for the given trace_id.
    Caller must validate tenant_id via context_guard before use.
    """
    async with _store_lock:
        all_events: List[Dict[str, Any]] = []
        for sid, events in _acontext_store.items():
            if sid.startswith("__") or not (sid == trace_id or sid.startswith(trace_id + ":")):
                continue
            for ev in events:
                p = ev.get("payload", {})
                tenant_in_payload = p.get("tenant_id") or (p.get("payload") or {}).get("tenant_id")
                if tenant_in_payload and tenant_in_payload != tenant_id:
                    continue  ***REMOVED*** skip cross-tenant
                all_events.append(ev)
        all_events.sort(key=lambda e: e.get("payload", {}).get("ts", ""))
        return all_events


def get_session_id_from_trace(trace_id: str, run_id: str = "") -> str:
    """Derive session_id from trace_id and optional run_id."""
    return f"{trace_id}:{run_id}" if run_id else trace_id


def store_event_sync(
    session_id: str,
    tenant_id: str,
    event_type: str,
    payload: dict,
    lead_id: Optional[str] = None,
) -> None:
    """
    Fire-and-forget sync wrapper for store_event.
    Used by UPAP gates (sync context). Non-blocking, best-effort.
    """
    import threading

    def _run() -> None:
        try:
            asyncio.run(store_event(session_id, tenant_id, event_type, payload, lead_id))
        except Exception as e:
            logger.debug("Acontext store_event_sync failed: %s", e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
