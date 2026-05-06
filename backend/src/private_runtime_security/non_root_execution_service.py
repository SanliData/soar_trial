"""
MODULE: non_root_execution_service
PURPOSE: Privilege boundary metadata — non-root preferred (H-043)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_non_root_execution_manifest() -> dict[str, Any]:
    return {
        "non_root_runtime_preferred": True,
        "privilege_levels": [
            {"name": "runtime_worker", "uid_policy": "non_zero_required", "capabilities": []},
            {"name": "tool_bridge", "uid_policy": "dedicated_low_priv_user", "capabilities": ["net_bind_low_ports_false"]},
        ],
        "isolated_execution_policies": ["readonly_app_image", "seccomp_allowlist_placeholder"],
        "explainable_privilege_metadata": True,
        "deterministic": True,
    }


def evaluate_non_root_compliance(*, process_uid_zero: bool) -> dict[str, Any]:
    return {
        "compliant_non_root": not process_uid_zero,
        "risk_if_root": "elevated_attack_surface",
        "deterministic": True,
    }
