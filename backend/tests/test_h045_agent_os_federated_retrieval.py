"""
TEST: H-045 agent OS, federated retrieval, NL control, selective context
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.agent_operating_system.agent_os_validation_service import validate_agent_record
from src.agent_operating_system.agent_permission_governance import evaluate_agent_permission_gate
from src.agent_operating_system.agent_registry_service import get_agent
from src.agent_operating_system.agent_role_service import export_agent_roles
from src.app import create_app
from src.federated_retrieval.connector_registry_service import export_connector_registry
from src.federated_retrieval.federated_search_service import federated_search
from src.federated_retrieval.incremental_sync_service import export_incremental_sync_status
from src.natural_language_control_plane.human_approval_service import classify_approval_requirement
from src.natural_language_control_plane.nl_command_parser import parse_nl_command
from src.selective_context_runtime.retrieval_budget_service import get_budget
from src.selective_context_runtime.selective_context_validation_service import validate_no_uncontrolled_retrieval_expansion
from src.selective_context_runtime.selective_expansion_service import decide_selective_expansion

os.environ.setdefault("JWT_SECRET", "test-h045-jwt-secret-32characters-required!")
os.environ.setdefault("SOARB2B_API_KEYS", "test-h045-key")

app = create_app()
client = TestClient(app)


def test_valid_agent_accepted():
    agent = get_agent("procurement_agent")
    validate_agent_record(agent)


def test_invalid_agent_rejected():
    bad = dict(get_agent("procurement_agent"))
    bad.pop("agent_id")
    with pytest.raises(ValueError):
        validate_agent_record(bad)


def test_role_permissions_deterministic():
    a = json.dumps(export_agent_roles(), sort_keys=True)
    b = json.dumps(export_agent_roles(), sort_keys=True)
    assert a == b


def test_high_risk_nl_command_requires_approval():
    parsed = parse_nl_command("Submit this to the external portal")
    assert parsed["risk_level"] == "high"
    appr = classify_approval_requirement(parsed_intent=parsed["parsed_intent"], risk_level=parsed["risk_level"])
    assert appr["human_approval_required"] is True


def test_connector_metadata_deterministic():
    a = json.dumps(export_connector_registry(), sort_keys=True)
    b = json.dumps(export_connector_registry(), sort_keys=True)
    assert a == b


def test_incremental_sync_status_deterministic():
    a = json.dumps(export_incremental_sync_status(), sort_keys=True)
    b = json.dumps(export_incremental_sync_status(), sort_keys=True)
    assert a == b


def test_federated_search_preserves_lineage():
    out = federated_search(query="telecom bid", mode="hybrid", limit=5)
    for r in out["results"]:
        assert "source_lineage" in r
        assert r["source_lineage"]["source_name"]


def test_relevance_policy_and_expansion_deterministic():
    chunks = [
        {"chunk_id": "c1", "text": "ISO 27001 net-30", "source_lineage": {"authority_score": 0.88, "freshness_days": 3}},
        {"chunk_id": "c2", "text": "marketing", "source_lineage": {"authority_score": 0.55, "freshness_days": 21}},
    ]
    a = decide_selective_expansion(workflow_name="procurement_analysis", query="ISO", chunks=chunks)
    b = decide_selective_expansion(workflow_name="procurement_analysis", query="ISO", chunks=chunks)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert "selected_chunk_ids" in a


def test_retrieval_budget_enforced_and_uncontrolled_rejected():
    b = get_budget("procurement_analysis")
    assert b["max_expanded_chunks"] > 0
    with pytest.raises(ValueError, match="unlimited retrieval expansion rejected"):
        validate_no_uncontrolled_retrieval_expansion({"unlimited_retrieval_expansion": True})


def test_autonomous_fleet_mutation_rejected_by_permission_gate():
    denied = evaluate_agent_permission_gate(
        agent_id="procurement_agent",
        requested_capability_id="context.types",
        workflow_scope="wrong_scope",
        high_risk_command=False,
        human_approval_present=False,
    )
    assert denied["allowed"] is False


def test_endpoints_smoke():
    r = client.get("/api/v1/system/agents")
    assert r.status_code == 200
    assert r.json()["agent_operating_system_foundation"] is True

    r2 = client.get("/api/v1/system/nl-control/intents")
    assert r2.status_code == 200
    assert r2.json()["unrestricted_nl_execution"] is False

    r3 = client.get("/api/v1/system/retrieval/connectors")
    assert r3.status_code == 200
    assert r3.json()["lineage_required"] is True

    r4 = client.get("/api/v1/system/selective-context/expansion")
    assert r4.status_code == 200
    assert r4.json()["rl_training_enabled"] is False

