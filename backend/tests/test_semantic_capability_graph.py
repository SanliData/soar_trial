"""
TEST: semantic_capability_graph (H-034)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.semantic_capability_graph.capability_topology_service import (
    list_dependency_paths,
    summarize_topology,
)
from src.semantic_capability_graph.capability_validation_service import (
    validate_capability_id,
    validate_relationship_triple,
    validate_topology_integrity,
    validate_trust_relationship,
)

os.environ.setdefault("JWT_SECRET", "test-h034-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h034-graph-key"

app = create_app()
client = TestClient(app)


def test_valid_capability_accepted():
    validate_capability_id("runtime_context")


def test_invalid_capability_rejected():
    with pytest.raises(ValueError, match="unknown semantic capability"):
        validate_capability_id("phantom_domain")


def test_topology_deterministic():
    a = json.dumps(summarize_topology(), sort_keys=True)
    b = json.dumps(summarize_topology(), sort_keys=True)
    assert a == b


def test_dependency_paths_deterministic():
    a = json.dumps(list_dependency_paths("workflow_governance"), sort_keys=True)
    b = json.dumps(list_dependency_paths("workflow_governance"), sort_keys=True)
    assert a == b


def test_semantic_contracts_validated():
    validate_topology_integrity()


def test_runtime_semantic_snapshots_deterministic():
    from src.semantic_capability_graph.capability_context_service import export_runtime_semantic_snapshot

    a = json.dumps(export_runtime_semantic_snapshot(), sort_keys=True)
    b = json.dumps(export_runtime_semantic_snapshot(), sort_keys=True)
    assert a == b


def test_invalid_relationship_rejected():
    with pytest.raises(ValueError):
        validate_relationship_triple("runtime_context", "depends_on", "phantom")


def test_trust_edge_ordered_pair():
    validate_trust_relationship("workflow_governance", "agent_security")


def test_api_graph_envelope():
    r = client.get("/api/v1/system/capabilities/graph")
    assert r.status_code == 200
    assert r.json().get("recursive_capability_mutation") is False


def test_api_topology():
    r = client.get("/api/v1/system/capabilities/topology")
    assert r.status_code == 200
    assert "summary" in r.json()


def test_h020_catalog_has_graph_extension():
    r = client.get("/api/v1/system/capabilities")
    assert r.status_code == 200
    assert r.json().get("semantic_capability_graph", {}).get("schema_version") == "h034_v1"
