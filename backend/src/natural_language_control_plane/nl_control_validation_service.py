"""
MODULE: nl_control_validation_service
PURPOSE: Validate NL control plane outputs and reject unsafe execution flags (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def validate_no_unrestricted_nl_execution(meta: dict[str, Any] | None) -> None:
    if not meta:
        return
    if meta.get("unrestricted_nl_execution") is True:
        raise ValueError("unrestricted NL execution rejected")
    if meta.get("natural_language_is_security_boundary") is True:
        raise ValueError("NL-as-security-boundary rejected")
    if meta.get("hidden_execution_permissions") is True:
        raise ValueError("hidden execution permissions rejected")


def validate_command_audit_record(rec: dict[str, Any]) -> None:
    if not isinstance(rec, dict):
        raise ValueError("invalid audit record")
    required = {
        "command_id",
        "raw_command_summary",
        "parsed_intent",
        "routed_workflow",
        "approval_required",
        "decision_status",
        "created_at",
    }
    if required - rec.keys():
        raise ValueError("audit record missing fields")

