"""
MODULE: mcp_gateway_registry
PURPOSE: Static governed MCP-style gateway registry — no unrestricted execution (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

GATEWAY_EPOCH = "2025-05-01T00:00:00Z"

***REMOVED*** Deterministic registry only — no runtime mutation API.
GATEWAYS: dict[str, dict[str, Any]] = {
    "browser_intelligence": {
        "gateway_name": "browser_intelligence",
        "capability_domain": "browser_automation",
        "execution_scope": "sandboxed_dom",
        "trust_level": "medium",
        "requires_human_approval": True,
        "sandbox_required": True,
        "provider_type": "governed_browser_surface",
        "created_at": GATEWAY_EPOCH,
    },
    "procurement_lookup": {
        "gateway_name": "procurement_lookup",
        "capability_domain": "procurement",
        "execution_scope": "read_only_http",
        "trust_level": "high",
        "requires_human_approval": False,
        "sandbox_required": True,
        "provider_type": "curated_http_adapter",
        "created_at": GATEWAY_EPOCH,
    },
    "contractor_verification": {
        "gateway_name": "contractor_verification",
        "capability_domain": "contractor_risk",
        "execution_scope": "read_only_http",
        "trust_level": "high",
        "requires_human_approval": True,
        "sandbox_required": True,
        "provider_type": "attribution_required_adapter",
        "created_at": GATEWAY_EPOCH,
    },
    "gis_enrichment": {
        "gateway_name": "gis_enrichment",
        "capability_domain": "geospatial",
        "execution_scope": "bounded_api",
        "trust_level": "medium",
        "requires_human_approval": False,
        "sandbox_required": True,
        "provider_type": "rate_limited_geo_adapter",
        "created_at": GATEWAY_EPOCH,
    },
    "document_extraction": {
        "gateway_name": "document_extraction",
        "capability_domain": "documents",
        "execution_scope": "ephemeral_parse",
        "trust_level": "medium",
        "requires_human_approval": False,
        "sandbox_required": True,
        "provider_type": "local_first_parser",
        "created_at": GATEWAY_EPOCH,
    },
}


def export_gateways_manifest() -> list[dict[str, Any]]:
    return [dict(GATEWAYS[k]) for k in sorted(GATEWAYS.keys())]


def get_gateway(name: str) -> dict[str, Any] | None:
    key = name.strip()
    if key not in GATEWAYS:
        return None
    return dict(GATEWAYS[key])
