"""
TEST: evolution_governance (H-036)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.app import create_app
from src.evolution_governance.evolution_trace_service import export_evolution_traces
from src.evolution_governance.evolution_validation_service import (
    SimulateRequest,
    validate_proposal_id,
    validate_unsafe_mutation_metadata,
)
from src.evolution_governance.mutation_proposal_service import MUTATION_PROPOSALS
from src.evolution_governance.rollback_governance_service import assess_rollback_readiness
from src.evolution_governance.sandbox_evaluation_service import evaluate_sandbox
from src.evolution_governance.workflow_mutation_service import simulate_workflow_mutation_for_proposal

os.environ.setdefault("JWT_SECRET", "test-h036-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h036-evolution-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/evolution"


def test_valid_mutation_proposal_accepted():
    validate_proposal_id("mut-wf-opt-001")
    assert "mut-wf-opt-001" in MUTATION_PROPOSALS


def test_invalid_proposal_rejected():
    with pytest.raises(ValueError, match="invalid mutation proposal"):
        validate_proposal_id("unknown-proposal")


def test_sandbox_evaluation_deterministic():
    a = json.dumps(evaluate_sandbox("mut-retry-001"), sort_keys=True)
    b = json.dumps(evaluate_sandbox("mut-retry-001"), sort_keys=True)
    assert a == b


def test_rollback_validation_enforced():
    r = assess_rollback_readiness(
        "mut-wf-opt-001",
        mutation_deployed=False,
        governance_approval_completed=True,
        evaluation_trace_stored=True,
    )
    assert r["rollback_ready"] is True
    r2 = assess_rollback_readiness(
        "mut-wf-opt-001",
        mutation_deployed=True,
        governance_approval_completed=True,
        evaluation_trace_stored=True,
    )
    assert r2["rollback_ready"] is False


def test_workflow_mutation_simulation_deterministic():
    a = json.dumps(simulate_workflow_mutation_for_proposal("mut-loop-001"), sort_keys=True)
    b = json.dumps(simulate_workflow_mutation_for_proposal("mut-loop-001"), sort_keys=True)
    assert a == b


def test_unsafe_mutations_rejected():
    with pytest.raises(ValueError):
        validate_unsafe_mutation_metadata({"autonomous_production_mutation": True})
    with pytest.raises(ValidationError):
        SimulateRequest.model_validate(
            {"proposal_id": "mut-wf-opt-001", "sandbox_only": False, "request_production_deploy": False}
        )


def test_governance_traces_deterministic():
    a = json.dumps(export_evolution_traces(), sort_keys=True)
    b = json.dumps(export_evolution_traces(), sort_keys=True)
    assert a == b


def test_api_proposals_envelope():
    r = client.get(f"{BASE}/proposals")
    assert r.status_code == 200
    body = r.json()
    assert body.get("unrestricted_runtime_self_modification") is False
    assert len(body["mutation_proposals"]) >= 5


def test_api_simulate():
    r = client.post(
        f"{BASE}/simulate",
        json={
            "proposal_id": "mut-prompt-001",
            "sandbox_only": True,
            "request_production_deploy": False,
        },
    )
    assert r.status_code == 200
    sim = r.json()["simulation"]
    assert sim["sandbox_only"] is True
    assert sim["prompt_comparison"] is not None


def test_api_simulate_rejects_deploy_flag():
    r = client.post(
        f"{BASE}/simulate",
        json={
            "proposal_id": "mut-wf-opt-001",
            "sandbox_only": True,
            "request_production_deploy": True,
        },
    )
    assert r.status_code == 422


def test_api_rollback_check():
    r = client.post(
        f"{BASE}/rollback-check",
        json={
            "proposal_id": "mut-wf-opt-001",
            "mutation_deployed": False,
            "governance_approval_completed": True,
            "evaluation_trace_stored": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["rollback"]["rollback_ready"] is True
