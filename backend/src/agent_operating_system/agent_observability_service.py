"""
MODULE: agent_observability_service
PURPOSE: Deterministic observability for agent OS layer (H-045)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_fleet_service import export_agent_fleet_status
from src.agentic_identity.cryptographic_identity_service import export_cryptographic_identities


def export_agent_observability_manifest() -> dict[str, Any]:
    fleet = export_agent_fleet_status()
    warnings = list(fleet.get("governance_warnings") or [])
    crypto = export_cryptographic_identities()
    return {
        "fleet": fleet,
        "observability": {
            "audit_traces_required": True,
            "autonomous_mutation": False,
            "unrestricted_nl_execution": False,
            # H-048 projections (observability only)
            "event_streaming_supported": True,
            "approval_streaming_supported": True,
            "conversational_evaluation_supported": True,
            # H-049 projections (identity governed)
            "identity_governed": True,
            "cryptographic_identity_metadata_supported": True,
            "identity_attribution_auditable": True,
        },
        "identity": {"cryptographic_identities": crypto["cryptographic_identities"], "deterministic": True},
        "warning_count": len(warnings),
        "warnings": warnings,
        "deterministic": True,
    }

