"""
MODULE: connector_freshness_risk
PURPOSE: Deterministic source freshness risk derived from H-046 connector freshness (H-047)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.system_visibility.connector_freshness_service import export_connector_freshness


def assess_source_freshness_risk() -> dict[str, Any]:
    conns = export_connector_freshness()["connectors"]
    bad = [c for c in conns if c["status"] in {"degraded", "disconnected"}]
    stale = [c for c in conns if c["status"] == "stale"]
    score = min(7, len(bad) * 2 + len(stale))
    return {
        "risk_score": int(score),
        "explain": {"degraded_or_disconnected": [c["connector_name"] for c in bad], "stale": [c["connector_name"] for c in stale]},
        "deterministic": True,
    }

