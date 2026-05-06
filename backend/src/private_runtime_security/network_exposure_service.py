"""
MODULE: network_exposure_service
PURPOSE: Unsafe exposure detection — detection only (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def assess_network_exposure(snapshot: dict[str, Any]) -> dict[str, Any]:
    flags: list[str] = []
    if snapshot.get("public_listen_ports"):
        flags.append("public_ports_detected")
    if snapshot.get("unrestricted_ingress_route"):
        flags.append("unrestricted_ingress")
    if snapshot.get("external_execution_escalation_route"):
        flags.append("external_execution_escalation")
    if snapshot.get("insecure_mesh_access"):
        flags.append("insecure_runtime_mesh_access")
    if snapshot.get("unsafe_execution_surface_exposed"):
        flags.append("unsafe_execution_surfaces")
    level = "nominal"
    if flags:
        level = "critical" if len(flags) >= 3 else "elevated"
    return {
        "exposure_risk_level": level,
        "flags": sorted(flags),
        "autonomous_network_shutdown": False,
        "detection_only": True,
        "deterministic": True,
    }


def export_network_exposure_manifest() -> dict[str, Any]:
    return {
        "examples": [
            assess_network_exposure({}),
            assess_network_exposure(
                {
                    "public_listen_ports": True,
                    "unrestricted_ingress_route": True,
                    "unsafe_execution_surface_exposed": True,
                }
            ),
        ],
        "deterministic": True,
    }
