"""
TEST: workflow_governance (H-032)
PURPOSE: Contracts, effort, delegation, decay, sessions, acceptance
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.workflow_governance.adaptive_effort_service import resolve_effort
from src.workflow_governance.context_decay_service import detect_context_rot
from src.workflow_governance.delegation_policy_service import validate_delegation
from src.workflow_governance.subagent_parallelization_service import validate_parallel_plan
from src.workflow_governance.workflow_acceptance_service import evaluate_acceptance
from src.workflow_governance.workflow_contract_registry import WORKFLOW_CONTRACTS
from src.workflow_governance.workflow_session_service import (
    create_session,
    get_governance_runtime_summary,
    summarize_session,
)
from src.workflow_governance.workflow_validation_service import validate_workflow_name

os.environ.setdefault("JWT_SECRET", "test-h032-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h032-wf-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/workflows"


def test_valid_workflow_contract_accepted():
    assert "procurement_analysis" in WORKFLOW_CONTRACTS
    validate_workflow_name("graph_investigation")


def test_invalid_workflow_rejected():
    with pytest.raises(ValueError, match="invalid workflow_name"):
        validate_workflow_name("unknown_workflow_xyz")


def test_adaptive_effort_deterministic():
    a = json.dumps(resolve_effort("x", workflow_name="graph_investigation"))
    b = json.dumps(resolve_effort("x", workflow_name="graph_investigation"))
    assert a == b


def test_delegation_policies_enforced():
    validate_delegation(
        workflow_name="procurement_analysis",
        delegate_to="worker_a",
        depth=1,
        permission="read:crm",
        current_subagent_count=0,
    )
    with pytest.raises(ValueError, match="out of bounds"):
        validate_delegation(
            workflow_name="procurement_analysis",
            delegate_to="worker_a",
            depth=5,
            permission="read:crm",
            current_subagent_count=0,
        )


def test_context_decay_detection_deterministic():
    a = json.dumps(detect_context_rot(10000, 20, "procurement_analysis"))
    b = json.dumps(detect_context_rot(10000, 20, "procurement_analysis"))
    assert a == b


def test_session_summaries_deterministic_for_state():
    out = create_session("opportunity_ranking", label="t")
    sid = out["session"]["session_id"]
    s1 = json.dumps(summarize_session(sid))
    s2 = json.dumps(summarize_session(sid))
    assert s1 == s2


def test_acceptance_validation_works():
    r = evaluate_acceptance(
        "procurement_analysis",
        {
            "requirements_matrix_present": 1,
            "risk_notes_present": 1,
            "next_steps_explicit": 1,
        },
        True,
        True,
    )
    assert r["accepted"] is True

    r2 = evaluate_acceptance(
        "procurement_analysis",
        {"requirements_matrix_present": 1},
        True,
        True,
    )
    assert r2["accepted"] is False


def test_runtime_summary_envelope():
    s = get_governance_runtime_summary()
    assert s["governance_envelope"]["recursive_workflow_swarm"] is False


def test_api_contracts_envelope():
    res = client.get(f"{BASE}/contracts")
    assert res.status_code == 200
    assert res.json().get("unrestricted_autonomous_execution") is False


def test_api_validate():
    res = client.post(
        f"{BASE}/validate",
        json={
            "workflow_name": "executive_briefing",
            "outputs": {
                "decision_block": 1,
                "risk_register": 1,
                "assumptions_explicit": 1,
            },
            "constraints_respected": True,
            "escalation_acknowledged": True,
        },
    )
    assert res.status_code == 200
    assert res.json()["acceptance"]["accepted"] is True


def test_parallel_plan_cap():
    validate_parallel_plan(2, "bounded_fanout")
    with pytest.raises(ValueError, match="exceeds cap"):
        validate_parallel_plan(5, "bounded_fanout")
