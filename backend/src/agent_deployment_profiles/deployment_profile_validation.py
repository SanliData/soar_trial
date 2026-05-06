"""
MODULE: deployment_profile_validation
PURPOSE: Validation for safe deployment profiles (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def reject_unrestricted_public_deployment(profile: dict[str, Any]) -> None:
    if profile.get("runtime_visibility") == "public":
        raise ValueError("public runtime visibility rejected for foundation")
    if profile.get("public_unrestricted_default") is True:
        raise ValueError("public unrestricted default rejected")


def require_identity_and_firewall_for_external(profile: dict[str, Any]) -> None:
    channels = set(profile.get("allowed_channels") or [])
    external = bool(channels - {"internal_web_ui"})
    if external:
        if profile.get("identity_required") is not True:
            raise ValueError("identity required for external channels")
        if profile.get("firewall_required") is not True:
            raise ValueError("firewall required for external channels")

