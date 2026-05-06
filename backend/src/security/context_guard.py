"""
SECURITY: Context guard
PURPOSE: Enforce tenant isolation for Acontext sessions.
ENCODING: UTF-8 WITHOUT BOM

Rules:
- All Acontext sessions must include tenant_id
- No cross-tenant session access allowed
- Validate before every get_messages()
- Reject if session.tenant_id != request.tenant_id
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ContextGuardError(Exception):
    """Raised when tenant isolation is violated."""

    pass


def validate_tenant_access(
    session_tenant_id: Optional[str],
    request_tenant_id: str,
    session_id: str = "",
) -> None:
    """
    Validate that request tenant matches session tenant.
    Raises ContextGuardError if cross-tenant access attempted.
    """
    if not request_tenant_id:
        raise ContextGuardError("request_tenant_id is required")
    if session_tenant_id is not None and session_tenant_id != request_tenant_id:
        logger.warning(
            "Context guard: cross-tenant access rejected session=%s session_tenant=%s request_tenant=%s",
            session_id, session_tenant_id, request_tenant_id,
        )
        raise ContextGuardError(
            f"Cross-tenant access not allowed: session tenant {session_tenant_id} != request tenant {request_tenant_id}"
        )


def require_tenant_in_session(session: Dict[str, Any]) -> str:
    """
    Ensure session includes tenant_id. Return tenant_id.
    Raises ContextGuardError if tenant_id missing.
    """
    tenant_id = session.get("tenant_id") or (session.get("payload") or {}).get("tenant_id")
    if not tenant_id:
        raise ContextGuardError("Session must include tenant_id")
    return str(tenant_id)


def extract_tenant_from_context(
    query_id: str = "",
    plan_id: str = "",
    created_by_user_id: Optional[int] = None,
) -> str:
    """
    Derive tenant_id from available context.
    Fallback: use plan_id or query_id as tenant for single-tenant setups.
    """
    if created_by_user_id is not None:
        return f"tenant:{created_by_user_id}"
    plan_or_query = plan_id or query_id
    if plan_or_query:
        ***REMOVED*** Use first 12 chars of plan_id as workspace-scoped tenant for isolation
        return f"plan:{plan_or_query[:24]}"
    return "default"
