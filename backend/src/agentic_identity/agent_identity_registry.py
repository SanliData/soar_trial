"""
MODULE: agent_identity_registry
PURPOSE: Explicit identity issuance registry (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.agentic_identity.identity_validation_service import (
    reject_hidden_identity_mutation,
    require_identity_lineage,
    validate_trust_level,
)

IDENTITY_EPOCH = "2026-01-01T00:00:00Z"

_REGISTRY: Dict[str, Dict[str, Any]] = {}
_ORDER: List[str] = []
_MAX = 100


def issue_identity(
    *,
    identity_id: str,
    agent_id: str,
    identity_type: str,
    capability_scope: list[str],
    workflow_scope: str,
    approval_scope: str,
    runtime_budget_scope: str,
    trust_level: str,
    tags: list[str] | None = None,
    issued_by: str = "identity_admin",
    issuance_reason: str = "explicit_issuance",
) -> dict[str, Any]:
    iid = (identity_id or "").strip()
    if not iid:
        raise ValueError("identity_id required")
    rec = {
        "identity_id": iid,
        "agent_id": (agent_id or "").strip(),
        "identity_type": (identity_type or "").strip() or "agent_identity",
        "capability_scope": list(capability_scope or []),
        "workflow_scope": (workflow_scope or "").strip() or "procurement_analysis",
        "approval_scope": (approval_scope or "").strip() or "hitl_required_for_high_risk",
        "runtime_budget_scope": (runtime_budget_scope or "").strip() or "bounded_budget_v1",
        "issued_at": IDENTITY_EPOCH,
        "expires_at": "2026-12-31T00:00:00Z",
        "trust_level": (trust_level or "").strip() or "moderate",
        "tags": sorted(list(tags or [])),
        "identity_lineage": {"issued_by": (issued_by or "").strip(), "issuance_reason": (issuance_reason or "").strip()},
        "hidden_identity_creation": False,
        "hidden_identity_escalation": False,
        "self_authorizing_agent": False,
        "deterministic": True,
    }
    validate_trust_level(rec["trust_level"])
    require_identity_lineage(rec)
    reject_hidden_identity_mutation(rec)

    if iid not in _REGISTRY:
        _ORDER.append(iid)
    _REGISTRY[iid] = rec
    while len(_ORDER) > _MAX:
        old = _ORDER.pop(0)
        _REGISTRY.pop(old, None)
    return dict(rec)


def export_identity_registry(*, limit: int = 50) -> dict[str, Any]:
    if not _REGISTRY:
        ***REMOVED*** Deterministic sample issuance for foundation.
        issue_identity(
            identity_id="id-001",
            agent_id="agent_procurement_reviewer",
            identity_type="agent_identity",
            capability_scope=["results.opportunities", "system.visibility.health"],
            workflow_scope="procurement_analysis",
            approval_scope="hitl_required_for_high_risk",
            runtime_budget_scope="bounded_budget_v1",
            trust_level="moderate",
            tags=["sample", "governed"],
        )
    lim = max(1, min(int(limit), 100))
    ids = list(_ORDER)[-lim:]
    rows = [dict(_REGISTRY[i]) for i in ids]
    return {"identities": rows, "identity_count": len(rows), "deterministic": True}

