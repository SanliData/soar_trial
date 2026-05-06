"""
MODULE: identity_validation_service
PURPOSE: Identity validation (no hidden creation/escalation) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def require_identity_lineage(identity: dict[str, Any]) -> None:
    lineage = identity.get("identity_lineage")
    if not isinstance(lineage, dict) or not lineage.get("issued_by") or not lineage.get("issuance_reason"):
        raise ValueError("identity lineage required")


def reject_hidden_identity_mutation(identity: dict[str, Any]) -> None:
    if identity.get("hidden_identity_creation") is True:
        raise ValueError("hidden identity creation rejected")
    if identity.get("hidden_identity_escalation") is True:
        raise ValueError("hidden identity escalation rejected")
    if identity.get("self_authorizing_agent") is True:
        raise ValueError("self-authorizing agent rejected")


def validate_trust_level(level: str) -> None:
    if (level or "").strip() not in {"low", "moderate", "elevated", "critical"}:
        raise ValueError("invalid trust_level")

