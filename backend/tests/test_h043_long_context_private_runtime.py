"""
TEST: H-043 long-context, private runtime security, ensemble governance
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.capability_gateway.provider_abstraction_service import export_providers_surfaces
from src.ensemble_governance.consensus_scoring_service import compute_consensus_scores, export_consensus_scoring_manifest
from src.ensemble_governance.multi_evaluator_service import export_multi_evaluator_manifest
from src.long_context_runtime.adaptive_context_loader import export_adaptive_context_loader_manifest
from src.long_context_runtime.context_pressure_service import classify_context_pressure, export_context_pressure_manifest
from src.long_context_runtime.long_context_validation_service import validate_long_context_intent
from src.long_context_runtime.sparse_activation_service import export_sparse_provider_metadata_manifest
from src.private_runtime_security.network_exposure_service import assess_network_exposure
from src.private_runtime_security.runtime_access_validation import validate_runtime_access_intent

os.environ.setdefault("JWT_SECRET", "test-h043-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h043-lc-key"

app = create_app()
client = TestClient(app)


def test_adaptive_loading_deterministic():
    a = json.dumps(export_adaptive_context_loader_manifest(), sort_keys=True)
    assert a == json.dumps(export_adaptive_context_loader_manifest(), sort_keys=True)


def test_context_pressure_deterministic():
    m = classify_context_pressure(
        {
            "context_window_tokens": 20000,
            "retrieval_doc_breadth": 8,
            "duplicated_blocks": 2,
            "reflection_share": 0.12,
            "orchestration_depth_hint": 3,
        }
    )
    assert m["deterministic"] is True
    assert json.dumps(export_context_pressure_manifest(), sort_keys=True) == json.dumps(
        export_context_pressure_manifest(), sort_keys=True
    )


def test_sparse_metadata_valid():
    man = export_sparse_provider_metadata_manifest()
    assert man["direct_provider_orchestration_mutation"] is False
    assert any(p["provider_name"] == "openai" for p in man["providers"])


def test_runtime_isolation_deterministic():
    r = client.get("/api/v1/system/runtime/isolation")
    assert r.status_code == 200
    body = r.json()
    assert body["public_runtime_exposure_default"] is False
    assert body["isolation"]["non_root_preferred"] is True


def test_unsafe_exposure_detected():
    out = assess_network_exposure({"public_listen_ports": True, "unrestricted_ingress_route": True})
    assert "public_ports_detected" in out["flags"]
    assert out["autonomous_network_shutdown"] is False


def test_consensus_scoring_deterministic():
    a = compute_consensus_scores((0.8, 0.82, 0.79))
    b = compute_consensus_scores((0.8, 0.82, 0.79))
    assert a == b
    assert json.dumps(export_consensus_scoring_manifest(), sort_keys=True) == json.dumps(
        export_consensus_scoring_manifest(), sort_keys=True
    )


def test_evaluator_variance_deterministic():
    man = export_multi_evaluator_manifest()
    assert man["hidden_evaluator_weighting"] is False
    assert abs(man["weight_sum"] - 1.0) < 0.001


def test_uncontrolled_exposure_rejected():
    with pytest.raises(ValueError, match="public ai runtime"):
        validate_runtime_access_intent({"expose_ai_runtime_publicly": True})
    with pytest.raises(ValueError, match="unrestricted long-context"):
        validate_long_context_intent({"unrestricted_long_context_workflows": True})


def test_api_context_ensemble_envelopes():
    c = client.get("/api/v1/system/context/pressure").json()
    assert c["unrestricted_long_context_loading"] is False
    assert client.get("/api/v1/system/context/partitions").status_code == 200
    assert client.get("/api/v1/system/context/sparse-providers").status_code == 200
    assert client.get("/api/v1/system/context/fallbacks").status_code == 200
    assert client.get("/api/v1/system/runtime/network-exposure").status_code == 200
    assert client.get("/api/v1/system/runtime/private-mesh").status_code == 200
    assert client.get("/api/v1/system/runtime/non-root").status_code == 200
    e = client.get("/api/v1/system/ensemble/evaluators").json()
    assert e["hidden_ensemble_weighting"] is False
    assert client.get("/api/v1/system/ensemble/consensus").status_code == 200
    assert client.get("/api/v1/system/ensemble/variance").status_code == 200
    assert client.get("/api/v1/system/ensemble/randomization").status_code == 200


def test_provider_sparse_metadata_surface():
    surf = export_providers_surfaces()
    assert "sparse_long_context_metadata_by_provider" in surf
    assert surf["metadata_only_no_auto_switch"] is True
    assert "openai" in surf["sparse_long_context_metadata_by_provider"]
