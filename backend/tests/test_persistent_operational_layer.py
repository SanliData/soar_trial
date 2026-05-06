"""
TEST: persistent_workspace + graph_intelligence + runtime_clustering (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.graph_intelligence.graph_validation_service import validate_graph_operation_intent, validate_traversal_depth
from src.graph_intelligence.hybrid_query_service import export_hybrid_query_plan_manifest
from src.graph_intelligence.relationship_traversal_service import export_relationship_traversal_manifest, plan_relationship_traversal
from src.persistent_workspace.scheduled_execution_service import export_scheduled_execution_manifest
from src.persistent_workspace.typed_state_registry import export_typed_state_registry_manifest
from src.persistent_workspace.workspace_validation_service import validate_no_recursive_memory_expansion, validate_state_type
from src.runtime_clustering.cluster_validation_service import validate_clustering_config, validate_semantic_batch
from src.runtime_clustering.embedding_cluster_service import export_embedding_cluster_manifest

os.environ.setdefault("JWT_SECRET", "test-h042-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h042-persist-key"

app = create_app()
client = TestClient(app)


def test_typed_state_deterministic():
    a = json.dumps(export_typed_state_registry_manifest(), sort_keys=True)
    b = json.dumps(export_typed_state_registry_manifest(), sort_keys=True)
    assert a == b


def test_scheduled_workflow_governance_deterministic():
    man = export_scheduled_execution_manifest()
    assert man["governed_scheduling_only"] is True
    for s in man["schedules"]:
        assert s["autonomous_infinite_execution"] is False
    assert json.dumps(man, sort_keys=True) == json.dumps(export_scheduled_execution_manifest(), sort_keys=True)


def test_graph_traversal_deterministic():
    p = plan_relationship_traversal(
        start_kind="contractor", relationship_goal="subcontractor_chains", requested_depth=10
    )
    assert p["effective_depth"] == 4  ***REMOVED*** capped
    a = json.dumps(export_relationship_traversal_manifest(), sort_keys=True)
    b = json.dumps(export_relationship_traversal_manifest(), sort_keys=True)
    assert a == b


def test_hybrid_query_deterministic():
    hq = export_hybrid_query_plan_manifest()
    assert all(not p["mandatory_graph_dependency"] for p in hq["plans"])
    assert json.dumps(hq, sort_keys=True) == json.dumps(export_hybrid_query_plan_manifest(), sort_keys=True)


def test_semantic_clustering_deterministic():
    ec = export_embedding_cluster_manifest()
    assert ec["giant_clustering_infra_required"] is False
    assert json.dumps(ec, sort_keys=True) == json.dumps(export_embedding_cluster_manifest(), sort_keys=True)


def test_invalid_persistence_rejected():
    with pytest.raises(ValueError, match="invalid state type"):
        validate_state_type("floating_state")


def test_recursive_expansion_rejected():
    with pytest.raises(ValueError, match="recursive memory"):
        validate_no_recursive_memory_expansion({"recursive_memory_expansion": True})
    with pytest.raises(ValueError, match="uncontrolled persistent"):
        validate_no_recursive_memory_expansion({"uncontrolled_persistent_execution": True})


def test_graph_validation_helpers():
    with pytest.raises(ValueError):
        validate_graph_operation_intent({"autonomous_graph_mutation": True})
    with pytest.raises(ValueError):
        validate_traversal_depth(0)


def test_cluster_validation():
    validate_semantic_batch({"max_items": 64})
    with pytest.raises(ValueError):
        validate_semantic_batch({"max_items": 2000})
    with pytest.raises(ValueError):
        validate_clustering_config({"unbounded_cluster_growth": True})


def test_api_workspace_envelope():
    r = client.get("/api/v1/system/workspace/state")
    assert r.status_code == 200
    body = r.json()
    assert body["uncontrolled_persistent_execution"] is False
    assert "workspace_state" in body


def test_api_schedules_graph_clustering():
    assert client.get("/api/v1/system/workspace/schedules").status_code == 200
    assert client.get("/api/v1/system/graph/traversals").status_code == 200
    g = client.get("/api/v1/system/graph/hybrid-query").json()
    assert g["autonomous_graph_mutation"] is False
    assert client.get("/api/v1/system/clustering/groups").status_code == 200
    assert client.get("/api/v1/system/clustering/semantic-batches").status_code == 200
