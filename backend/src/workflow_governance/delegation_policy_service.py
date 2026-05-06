"""
MODULE: delegation_policy_service
PURPOSE: Explicit delegation gates — bounded depth and capability checks (H-032)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any

from src.workflow_governance.workflow_contract_registry import WORKFLOW_CONTRACTS

MAX_DELEGATION_DEPTH: int = 2
MAX_SUBAGENTS_PER_WORKFLOW: int = 4   # aligned with agent harness foundation cap


def validate_delegation(
    *,
    workflow_name: str,
    delegate_to: str,
    depth: int,
    permission: str,
    current_subagent_count: int,
) -> dict[str, Any]:
    if workflow_name not in WORKFLOW_CONTRACTS:
        raise ValueError(f"unknown workflow for delegation: {workflow_name}")
    if depth < 0 or depth > MAX_DELEGATION_DEPTH:
        raise ValueError(f"delegation depth out of bounds: {depth} (max {MAX_DELEGATION_DEPTH})")
    if not delegate_to or not delegate_to.strip():
        raise ValueError("delegate_to must be explicit — empty not permitted")
    if not permission or not str(permission).strip():
        raise ValueError("permission must be explicit")
    perm = str(permission).strip()
    if not perm.startswith(("read:", "execute:", "delegate:")):
        raise ValueError("permission must use approved prefixes (read:, execute:, delegate:)")
    contract = WORKFLOW_CONTRACTS[workflow_name]
    allowed = set(contract.get("allowed_tools") or [])
    if perm not in allowed:
        raise ValueError(f"permission not in contract allowed_tools: {perm}")
    if current_subagent_count >= MAX_SUBAGENTS_PER_WORKFLOW:
        raise ValueError("subagent limit reached for this workflow session")

    return {
        "delegation_ok": True,
        "depth": depth,
        "max_depth": MAX_DELEGATION_DEPTH,
        "subagent_cap": MAX_SUBAGENTS_PER_WORKFLOW,
        "hidden_escalation": False,
        "policy_version": "delegation_v1",
    }


def describe_delegation_policies() -> dict[str, Any]:
    return {
        "max_delegation_depth": MAX_DELEGATION_DEPTH,
        "max_subagents_per_workflow": MAX_SUBAGENTS_PER_WORKFLOW,
        "explicit_delegate_target_required": True,
        "notes": "No hidden escalation — all delegation requires explicit target and permission.",
    }
