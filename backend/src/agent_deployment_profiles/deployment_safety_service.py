"""
MODULE: deployment_safety_service
PURPOSE: Deterministic safety scoring for deployment profiles (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.agent_deployment_profiles.deployment_profile_registry import export_deployment_profiles


def _level(points: int) -> str:
    if points <= 0:
        return "low"
    if points <= 2:
        return "moderate"
    if points <= 5:
        return "elevated"
    return "critical"


def score_deployment_profile(profile: dict[str, Any]) -> dict[str, Any]:
    points = 0
    explain = []
    if profile.get("runtime_visibility") == "public":
        points += 6
        explain.append("public exposure")
    if profile.get("identity_required") is not True:
        points += 4
        explain.append("missing identity attribution")
    if profile.get("firewall_required") is not True:
        points += 3
        explain.append("missing firewall requirement")
    channels = set(profile.get("allowed_channels") or [])
    if bool(channels - {"internal_web_ui"}):
        points += 2
        explain.append("external channel enabled")
    if profile.get("human_approval_required") is not True:
        points += 1
        explain.append("missing approval checkpoints (recommended)")
    lvl = _level(points)
    return {"profile_id": profile.get("profile_id"), "risk_points": int(points), "risk_level": lvl, "explain": explain, "deterministic": True}


def export_deployment_safety() -> dict[str, Any]:
    profiles = export_deployment_profiles()["deployment_profiles"]
    rows = [score_deployment_profile(p) for p in profiles]
    rows.sort(key=lambda r: r["profile_id"])
    return {"deployment_safety": rows, "deterministic": True, "explainable": True}

