"""
MODULE: workflow_acceptance_service
PURPOSE: Check workflow completion against static contract criteria (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.workflow_governance.workflow_contract_registry import WORKFLOW_CONTRACTS


def evaluate_acceptance(
    workflow_name: str,
    outputs: dict[str, Any],
    constraints_respected: bool,
    escalation_acknowledged: bool,
) -> dict[str, Any]:
    if workflow_name not in WORKFLOW_CONTRACTS:
        raise ValueError(f"unknown workflow: {workflow_name}")
    contract = WORKFLOW_CONTRACTS[workflow_name]
    criteria = list(contract.get("acceptance_criteria") or [])
    present_keys = set(outputs.keys()) if isinstance(outputs, dict) else set()
    missing = [c for c in criteria if c not in present_keys]
    accepted = (
        not missing
        and constraints_respected
        and escalation_acknowledged
    )
    return {
        "accepted": accepted,
        "missing_outputs": missing,
        "constraints_respected": constraints_respected,
        "escalation_acknowledged": escalation_acknowledged,
        "acceptance_rule": "criteria_keys_present_v1",
    }
