"""
MODULE: kv_cache_registry
PURPOSE: KV cache metadata only — no uncontrolled reuse (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

_REGISTRY_EPOCH = "2025-05-01T00:00:00Z"

KV_CACHE_REGISTRY: list[dict[str, Any]] = [
    {
        "workflow_name": "lead_generation_v1",
        "cache_scope": "workspace_session_bound",
        "context_signature": "sha256:canonical_lead_ctx_v1",
        "reuse_allowed": True,
        "estimated_token_savings": 4200,
        "expiration_policy": "session_end_or_24h",
        "created_at": _REGISTRY_EPOCH,
    },
    {
        "workflow_name": "graph_readonly_explain",
        "cache_scope": "read_only_projection",
        "context_signature": "sha256:graph_path_ctx_v2",
        "reuse_allowed": True,
        "estimated_token_savings": 1800,
        "expiration_policy": "ttl_1h",
        "created_at": _REGISTRY_EPOCH,
    },
    {
        "workflow_name": "browser_compliance_check",
        "cache_scope": "firewall_policy_snapshot",
        "context_signature": "sha256:fw_policy_v3",
        "reuse_allowed": False,
        "estimated_token_savings": 0,
        "expiration_policy": "no_cache_stale_risk",
        "created_at": _REGISTRY_EPOCH,
    },
]


def export_kv_cache_registry_manifest() -> dict[str, Any]:
    return {
        "entries": [dict(e) for e in KV_CACHE_REGISTRY],
        "metadata_only": True,
        "uncontrolled_cache_reuse": False,
        "deterministic": True,
    }
