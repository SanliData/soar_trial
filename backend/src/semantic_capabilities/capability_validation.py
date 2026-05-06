"""
MODULE: capability_validation
PURPOSE: Deterministic validators for curated capability declarations (H-020)
ENCODING: UTF-8 WITHOUT BOM
"""

import json
import re
from typing import Any

from src.semantic_capabilities.capability_schema import CapabilityDefinition

_APPROVAL_SEMANTICS_IDS = frozenset(
    {
        "exposure.create",
        "onboarding.create_plan",
        "route_export.create_visit_route",
    }
)

_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sk_live_[a-zA-Z0-9]+"), "stripe_live"),
    (re.compile(r"(?i)bearer\s+[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+"), "jwt_blob"),
    (re.compile(r"(?i)postgresql://[^\s\"']+"), "database_url_like"),
)


def validate_capability_definitions(caps: list[CapabilityDefinition]) -> None:
    """
    Structural + governance checks for any capability list before publication.
    """
    if not caps:
        raise ValueError("capability list may not be empty")

    identifiers = [c.capability_id for c in caps]
    if len(identifiers) != len(set(identifiers)):
        duplicated = sorted({cid for cid in identifiers if identifiers.count(cid) > 1})
        raise ValueError(f"duplicate capability_id entries: {duplicated}")

    for cap in caps:
        if cap.destructive_action:
            if not cap.human_approval_required:
                raise ValueError(
                    f"{cap.capability_id}: destructive_action requires human_approval_required"
                )
            if cap.orchestration_safe:
                raise ValueError(
                    f"{cap.capability_id}: destructive_action must not mark orchestration_safe"
                )

        if cap.capability_id in _APPROVAL_SEMANTICS_IDS and not cap.human_approval_required:
            raise ValueError(
                f"{cap.capability_id}: exposures, onboarding launches, "
                "and route exports must require human approval metadata"
            )


def audit_export_json_for_secret_material(payload: dict[str, Any]) -> None:
    """
    Lightweight guardrail: fail if capability export JSON looks like leaked material.
    """
    blob = json.dumps(payload)
    lowered = blob.lower()

    sniffers = (
        "jwt_secret",
        "soarb2b_api_keys",
        "openai_api_key",
        "stripe_secret",
        "database_url",
        "google_client_secret",
        "postgresql://",
        "mongodb+srv://",
        "BEGIN RSA PRIVATE KEY",
        "PRIVATE KEY-----",
        "pwd=",
        "password=",
    )
    for needle in sniffers:
        if needle in lowered:
            raise ValueError(f"export_audit_failed: substring {needle}")

    for rg, label in _SECRET_PATTERNS:
        if rg.search(blob):
            raise ValueError(f"export_audit_failed: pattern matched ({label})")
