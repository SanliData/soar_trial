"""
TEST: spec_verification_governance (H-035)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.spec_verification_governance.architecture_contract_service import (
    ARCHITECTURE_CONTRACTS,
    export_architecture_contracts,
)
from src.spec_verification_governance.spec_validation_service import validate_spec_id
from src.spec_verification_governance.specification_registry import SPECIFICATIONS
from src.spec_verification_governance.trace_to_eval_service import map_trace_to_eval
from src.spec_verification_governance.validation_agent_service import enforce_isolated_validation
from src.spec_verification_governance.acceptance_criteria_service import validate_acceptance
from src.spec_verification_governance.review_governance_service import export_review_status

os.environ.setdefault("JWT_SECRET", "test-h035-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h035-spec-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/specs"


def test_valid_specification_accepted():
    assert "workflow_validation" in SPECIFICATIONS
    validate_spec_id("graph_investigation")


def test_invalid_specification_rejected():
    with pytest.raises(ValueError, match="invalid specification"):
        validate_spec_id("unknown_spec_xyz")


def test_acceptance_validation_deterministic():
    outputs = {k: True for k in SPECIFICATIONS["procurement_analysis"]["acceptance_criteria"]}
    a = json.dumps(
        validate_acceptance(
            "procurement_analysis",
            outputs,
            constraints_respected=True,
            escalation_acknowledged=True,
            architecture_contracts_ok=True,
        ),
        sort_keys=True,
    )
    b = json.dumps(
        validate_acceptance(
            "procurement_analysis",
            outputs,
            constraints_respected=True,
            escalation_acknowledged=True,
            architecture_contracts_ok=True,
        ),
        sort_keys=True,
    )
    assert a == b


def test_architecture_contracts_enforced():
    data = export_architecture_contracts()
    assert data["contract_count"] == len(ARCHITECTURE_CONTRACTS)


def test_trace_to_eval_deterministic():
    a = json.dumps(map_trace_to_eval("workflow_failure", "acceptance"), sort_keys=True)
    b = json.dumps(map_trace_to_eval("workflow_failure", "acceptance"), sort_keys=True)
    assert a == b


def test_isolated_validation_agents_enforced():
    enforce_isolated_validation(context_payload_chars=1000, permission="validation:spec", delegation_depth=0)
    with pytest.raises(ValueError):
        enforce_isolated_validation(context_payload_chars=100_000, permission="validation:x", delegation_depth=0)


def test_governance_review_deterministic():
    a = json.dumps(export_review_status(), sort_keys=True)
    b = json.dumps(export_review_status(), sort_keys=True)
    assert a == b


def test_api_specs_envelope():
    r = client.get(BASE)
    assert r.status_code == 200
    assert r.json().get("autonomous_architecture_mutation") is False


def test_api_trace_to_eval():
    r = client.post(
        f"{BASE}/trace-to-eval",
        json={"trace_category": "hallucinated_outputs", "trace_code": "contractor_fit"},
    )
    assert r.status_code == 200
    assert r.json()["trace_to_eval"]["autonomous_rule_mutation"] is False


def test_api_validate():
    crit = SPECIFICATIONS["onboarding_generation"]["acceptance_criteria"]
    r = client.post(
        f"{BASE}/validate",
        json={
            "spec_id": "onboarding_generation",
            "outputs": {k: 1 for k in crit},
            "constraints_respected": True,
            "escalation_acknowledged": True,
            "architecture_contracts_ok": True,
        },
    )
    assert r.status_code == 200
    assert r.json()["acceptance"]["accepted"] is True
