"""
MODULE: deployment_profile_registry
PURPOSE: Safe agent deployment profiles (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_deployment_profiles.deployment_profile_validation import (
    reject_unrestricted_public_deployment,
    require_identity_and_firewall_for_external,
)

DEPLOY_EPOCH = "2026-01-01T00:00:00Z"


def export_deployment_profiles() -> dict[str, Any]:
    profiles = [
        {
            "profile_id": "private_internal_agent",
            "profile_name": "Private internal agent (UI only)",
            "runtime_visibility": "private",
            "allowed_channels": ["internal_web_ui"],
            "private_runtime_required": True,
            "human_approval_required": False,
            "identity_required": True,
            "firewall_required": True,
            "created_at": DEPLOY_EPOCH,
            "deterministic": True,
        },
        {
            "profile_id": "governed_slack_agent",
            "profile_name": "Governed Slack agent (approval + identity)",
            "runtime_visibility": "private",
            "allowed_channels": ["slack"],
            "private_runtime_required": True,
            "human_approval_required": True,
            "identity_required": True,
            "firewall_required": True,
            "created_at": DEPLOY_EPOCH,
            "deterministic": True,
        },
        {
            "profile_id": "approval_required_research_agent",
            "profile_name": "Approval-required research agent",
            "runtime_visibility": "private",
            "allowed_channels": ["internal_web_ui"],
            "private_runtime_required": True,
            "human_approval_required": True,
            "identity_required": True,
            "firewall_required": True,
            "created_at": DEPLOY_EPOCH,
            "deterministic": True,
        },
        {
            "profile_id": "read_only_procurement_agent",
            "profile_name": "Read-only procurement agent",
            "runtime_visibility": "private",
            "allowed_channels": ["internal_web_ui", "slack"],
            "private_runtime_required": True,
            "human_approval_required": True,
            "identity_required": True,
            "firewall_required": True,
            "created_at": DEPLOY_EPOCH,
            "deterministic": True,
        },
    ]
    for p in profiles:
        p["public_unrestricted_default"] = False
        reject_unrestricted_public_deployment(p)
        require_identity_and_firewall_for_external(p)
    profiles.sort(key=lambda x: x["profile_id"])
    return {"deployment_profiles": profiles, "deterministic": True, "no_public_unrestricted_default": True}

