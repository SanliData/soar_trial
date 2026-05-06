"""
MODULE: compression_resilience_service
PURPOSE: Security rules resilient to context compression — proxy enforcement metadata (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_compression_resilience_manifest() -> dict[str, Any]:
    return {
        "security_rules_storage": "out_of_context_registry",
        "compression_safe_enforcement": True,
        "context_only_security_insufficient": True,
        "proxy_enforcement_mandatory": True,
        "runtime_persistence_validation": "static_manifest_checksum_v1",
        "deterministic": True,
    }
