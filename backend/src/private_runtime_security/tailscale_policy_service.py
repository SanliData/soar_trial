"""
MODULE: tailscale_policy_service
PURPOSE: Trusted overlay governance metadata — Tailscale-oriented (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_tailscale_policy_manifest() -> dict[str, Any]:
    return {
        "tailscale_only_access_profiles": ["internal_operator_mesh", "break_glass_human"],
        "overlay_trust_metadata": {
            "device_posture_checks": ["tag:governed-runtime", "mfa-required-group"],
            "split_dns_preferred_for_vendor_api": True,
        },
        "restricted_operational_paths": ["/infer", "/orchestration", "/retrieval-internal"],
        "metadata_only": True,
        "hidden_networking_mutation": False,
        "deterministic": True,
    }
