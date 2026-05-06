"""
MODULE: acceptance_criteria_service
PURPOSE: Deterministic acceptance checks against static specs (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.spec_verification_governance.specification_registry import get_specification


def validate_acceptance(
    spec_id: str,
    outputs: dict[str, Any],
    *,
    constraints_respected: bool,
    escalation_acknowledged: bool,
    architecture_contracts_ok: bool,
) -> dict[str, Any]:
    spec = get_specification(spec_id)
    criteria = list(spec.get("acceptance_criteria") or [])
    present = set(outputs.keys()) if isinstance(outputs, dict) else set()
    missing = [c for c in criteria if c not in present]
    accepted = (
        not missing
        and constraints_respected
        and escalation_acknowledged
        and architecture_contracts_ok
    )
    return {
        "accepted": accepted,
        "missing_outputs": missing,
        "constraints_respected": constraints_respected,
        "escalation_acknowledged": escalation_acknowledged,
        "architecture_contracts_ok": architecture_contracts_ok,
        "rule": "criteria_key_presence_v1",
    }
