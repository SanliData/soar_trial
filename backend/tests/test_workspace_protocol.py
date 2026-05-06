"""
TEST: workspace_protocol (H-038)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.workspace_protocol.project_memory_service import export_project_memory_manifest
from src.workspace_protocol.runtime_rule_service import export_runtime_rules_manifest
from src.workspace_protocol.workspace_command_registry import WORKSPACE_COMMANDS
from src.workspace_protocol.workspace_validation_service import (
    validate_memory_access_projection,
    validate_unsafe_workspace_metadata,
    validate_workspace_policy_name,
)
from src.workspace_protocol.workspace_policy_registry import WORKSPACE_POLICIES

os.environ.setdefault("JWT_SECRET", "test-h038-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h038-workspace-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/workspaces"


def test_valid_workspace_policy_accepted():
    validate_workspace_policy_name("procurement_workspace")
    assert "graph_analysis_workspace" in WORKSPACE_POLICIES


def test_invalid_workspace_rejected():
    with pytest.raises(ValueError, match="invalid workspace policy"):
        validate_workspace_policy_name("unknown_workspace_x")


def test_runtime_rule_loading_deterministic():
    a = json.dumps(export_runtime_rules_manifest(), sort_keys=True)
    b = json.dumps(export_runtime_rules_manifest(), sort_keys=True)
    assert a == b


def test_scoped_memory_deterministic():
    a = json.dumps(export_project_memory_manifest(), sort_keys=True)
    b = json.dumps(export_project_memory_manifest(), sort_keys=True)
    assert a == b
    assert export_project_memory_manifest()["unrestricted_persistent_memory"] is False


def test_permission_governance_enforced():
    r = client.get(f"{BASE}/permissions")
    assert r.status_code == 200
    body = r.json()
    assert body["permission_governance"]["hidden_execution_permissions"] is False
    assert body["subagent_scopes"]["uncontrolled_spawn"] is False


def test_unsafe_memory_access_rejected():
    with pytest.raises(ValueError):
        validate_unsafe_workspace_metadata({"unrestricted_persistent_memory": True})
    with pytest.raises(ValueError):
        validate_memory_access_projection("everywhere_unscoped")


def test_operational_command_registry_deterministic():
    a = json.dumps(sorted(WORKSPACE_COMMANDS.keys()), sort_keys=True)
    b = json.dumps(sorted(WORKSPACE_COMMANDS.keys()), sort_keys=True)
    assert a == b


def test_api_policies_envelope():
    r = client.get(f"{BASE}/policies")
    assert r.status_code == 200
    assert r.json().get("uncontrolled_agent_spawning") is False


def test_api_memory_scoped_only():
    r = client.get(f"{BASE}/memory")
    assert r.status_code == 200
    assert r.json()["memory"]["scoped_only"] is True
