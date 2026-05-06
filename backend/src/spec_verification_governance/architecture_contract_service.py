"""
MODULE: architecture_contract_service
PURPOSE: Declarative architecture rules — deterministic enforcement metadata (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

ARCHITECTURE_CONTRACTS: tuple[dict[str, Any], ...] = (
    {
        "contract_id": "arch_router_thin_v1",
        "rule": "routers contain no business logic",
        "enforcement": "code_review_plus_verify_script",
        "severity": "high",
    },
    {
        "contract_id": "arch_no_secrets_v1",
        "rule": "no secrets exposed in manifests or exports",
        "enforcement": "audit_export_json_for_secret_material",
        "severity": "critical",
    },
    {
        "contract_id": "arch_no_unrestricted_orch_v1",
        "rule": "no unrestricted orchestration expansion in foundation APIs",
        "enforcement": "envelope_flags_and_caps",
        "severity": "high",
    },
    {
        "contract_id": "arch_deterministic_workflows_v1",
        "rule": "deterministic workflows required for governance endpoints",
        "enforcement": "static_registry_and_pure_functions",
        "severity": "medium",
    },
)


def export_architecture_contracts() -> dict[str, Any]:
    return {
        "contracts": list(ARCHITECTURE_CONTRACTS),
        "contract_count": len(ARCHITECTURE_CONTRACTS),
        "autonomous_mutation": False,
    }


def check_architecture_contract_ids(reference: str) -> bool:
    return reference in {c["contract_id"] for c in ARCHITECTURE_CONTRACTS}
