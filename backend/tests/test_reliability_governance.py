"""
TEST: reliability_governance (H-033)
PURPOSE: Deterministic scoring and validation gates
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.reliability_governance.context_stability_service import export_context_stability
from src.reliability_governance.drift_monitoring_service import export_drift_report
from src.reliability_governance.embedding_health_service import export_embedding_health
from src.reliability_governance.retrieval_quality_service import export_retrieval_quality
from src.reliability_governance.reliability_validation_service import validate_ratio
from src.reliability_governance.workflow_reliability_service import export_workflow_reliability

os.environ.setdefault("JWT_SECRET", "test-h033-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h033-rel-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/reliability"


def test_drift_detection_deterministic():
    m = {
        "retrieval_drift_signal": 0.2,
        "graph_drift_signal": 0.1,
        "prompt_drift_signal": 0.0,
        "workflow_drift_signal": 0.05,
        "embedding_drift_signal": 0.15,
        "context_drift_signal": 0.08,
    }
    a = json.dumps(export_drift_report(m))
    b = json.dumps(export_drift_report(m))
    assert a == b


def test_embedding_freshness_valid():
    h = export_embedding_health(stale_ratio=0.02, missing_ratio=0.01, max_age_hours=24.0)
    assert 0.0 <= h["embedding_health_score"] <= 1.0


def test_retrieval_quality_scoring_deterministic():
    a = json.dumps(
        export_retrieval_quality(
            duplicate_ratio=0.1,
            stale_context_ratio=0.05,
            low_authority_ratio=0.0,
            weak_graph_link_ratio=0.02,
            relevance_decay=0.03,
        )
    )
    b = json.dumps(
        export_retrieval_quality(
            duplicate_ratio=0.1,
            stale_context_ratio=0.05,
            low_authority_ratio=0.0,
            weak_graph_link_ratio=0.02,
            relevance_decay=0.03,
        )
    )
    assert a == b


def test_workflow_reliability_scoring_deterministic():
    a = json.dumps(
        export_workflow_reliability(
            token_estimate=10000,
            retry_count=2,
            delegation_flap_count=1,
            acceptance_failure_ratio=0.05,
            context_rot_score=0.2,
        )
    )
    b = json.dumps(
        export_workflow_reliability(
            token_estimate=10000,
            retry_count=2,
            delegation_flap_count=1,
            acceptance_failure_ratio=0.05,
            context_rot_score=0.2,
        )
    )
    assert a == b


def test_context_stability_deterministic():
    a = json.dumps(export_context_stability(rot_score=0.4, context_chars=50000))
    b = json.dumps(export_context_stability(rot_score=0.4, context_chars=50000))
    assert a == b


def test_invalid_governance_metadata_rejected():
    with pytest.raises(ValueError):
        validate_ratio("x", 1.5)
    r = client.get(f"{BASE}/drift?retrieval_drift_signal=2")
    assert r.status_code == 422


def test_api_drift_envelope():
    r = client.get(f"{BASE}/drift")
    assert r.status_code == 200
    assert r.json().get("distributed_observability_mesh") is False


def test_api_traces_contains_examples():
    r = client.get(f"{BASE}/traces")
    assert r.status_code == 200
    obs = r.json()["observability"]["traces"]
    assert len(obs) >= 5
