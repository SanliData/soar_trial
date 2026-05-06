"""
TEST: skill_runtime (H-040)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.skill_runtime.dynamic_skill_loader import plan_skill_load
from src.skill_runtime.skill_activation_service import describe_activation_trace, export_skill_activation_manifest
from src.skill_runtime.skill_context_optimizer import export_context_optimization_manifest
from src.skill_runtime.skill_dependency_service import validate_dependency_closure, validate_skill_inheritance
from src.skill_runtime.skill_execution_trace_service import export_skill_execution_traces
from src.skill_runtime.skill_permission_service import evaluate_skill_permission_gate
from src.skill_runtime.skill_validation_service import validate_skill_name, validate_unsafe_skill_runtime_metadata

os.environ.setdefault("JWT_SECRET", "test-h040-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h040-skill-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/skills"


def test_valid_skill_accepted():
    validate_skill_name("procurement_review")


def test_invalid_skill_rejected():
    with pytest.raises(ValueError, match="invalid skill"):
        validate_skill_name("unknown_skill_xyz")


def test_deterministic_activation_manifest():
    a = json.dumps(export_skill_activation_manifest(), sort_keys=True)
    b = json.dumps(export_skill_activation_manifest(), sort_keys=True)
    assert a == b


def test_permission_enforcement_deterministic():
    g = evaluate_skill_permission_gate("graph_investigator", principal_permissions_ok=False)
    assert g["allowed"] is False
    assert json.dumps(
        evaluate_skill_permission_gate("graph_investigator", principal_permissions_ok=True),
        sort_keys=True,
    ) == json.dumps(
        evaluate_skill_permission_gate("graph_investigator", principal_permissions_ok=True),
        sort_keys=True,
    )


def test_dependency_validation_deterministic():
    validate_dependency_closure("graph_investigator")
    validate_dependency_closure("browser_compliance")


def test_unsafe_inheritance_rejected():
    with pytest.raises(ValueError, match="unsafe skill inheritance"):
        validate_skill_inheritance("*", "procurement_review")


def test_context_optimization_deterministic():
    a = json.dumps(export_context_optimization_manifest(), sort_keys=True)
    b = json.dumps(export_context_optimization_manifest(), sort_keys=True)
    assert a == b


def test_plan_load_respects_scope():
    ok = plan_skill_load(
        "procurement_review",
        activation_intent="explicit_command",
        runtime_scope="procurement_workspace",
        principal_permissions_ok=True,
    )
    assert ok["load_allowed"] is True
    bad = plan_skill_load(
        "procurement_review",
        activation_intent="explicit_command",
        runtime_scope="wrong_scope",
        principal_permissions_ok=True,
    )
    assert bad["load_allowed"] is False


def test_execution_traces_deterministic():
    assert json.dumps(export_skill_execution_traces(), sort_keys=True) == json.dumps(
        export_skill_execution_traces(), sort_keys=True
    )


def test_unsafe_metadata_rejected():
    with pytest.raises(ValueError):
        validate_unsafe_skill_runtime_metadata({"unrestricted_skill_spawning": True})


def test_describe_activation_trace_deterministic():
    a = json.dumps(describe_activation_trace("reliability_audit", "explicit_command"), sort_keys=True)
    b = json.dumps(describe_activation_trace("reliability_audit", "explicit_command"), sort_keys=True)
    assert a == b


def test_api_skills_envelope():
    r = client.get(BASE)
    assert r.status_code == 200
    body = r.json()
    assert body.get("unrestricted_skill_spawning") is False
    assert len(body["skills"]) >= 5


def test_api_permissions_manifest():
    r = client.get(f"{BASE}/permissions")
    assert r.status_code == 200
    assert r.json()["permissions"]["least_privilege_enforced"] is True
