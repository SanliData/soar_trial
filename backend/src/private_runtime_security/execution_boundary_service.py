"""
MODULE: execution_boundary_service
PURPOSE: Execution boundary manifests for private runtimes (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_execution_boundary_manifest() -> dict[str, Any]:
    return {
        "boundaries": [
            {"name": "infer_sandbox", "allows_outbound_internet": False, "tool_socket_access": "deny_by_default"},
            {"name": "orchestration_core", "allows_outbound_internet": "policy_governed_only", "tool_socket_access": "allowlist"},
        ],
        "autonomous_boundary_expansion": False,
        "deterministic": True,
    }
