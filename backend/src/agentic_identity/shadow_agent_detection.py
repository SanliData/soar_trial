"""
MODULE: shadow_agent_detection
PURPOSE: Shadow agent / attribution gap detection (detection-only) (H-049)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_operating_system.agent_registry_service import export_agent_registry
from src.agentic_identity.agent_identity_registry import export_identity_registry


def _risk_level(points: int) -> str:
    if points <= 0:
        return "low"
    if points <= 2:
        return "moderate"
    if points <= 5:
        return "elevated"
    return "critical"


def export_shadow_agent_detection() -> dict[str, Any]:
    agents = export_agent_registry()["agents"]
    identities = export_identity_registry()["identities"]
    known_agent_ids = {i["agent_id"] for i in identities if i.get("agent_id")}
    unmanaged = [a["agent_id"] for a in agents if a["agent_id"] not in known_agent_ids]

    points = len(unmanaged)
    out = {
        "unmanaged_agents": sorted(unmanaged),
        "unknown_runtime_identities": [],   # foundation: registry-only, no external ingest
        "unauthorized_mcp_projections": [],
        "orphaned_workflows": [],
        "suspicious_capability_escalation": [],
        "risk_level": _risk_level(points),
        "detection_only": True,
        "no_autonomous_shutdown": True,
        "deterministic": True,
    }
    return out

