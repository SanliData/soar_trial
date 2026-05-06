"""
TEST: inference_runtime (H-041)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.inference_runtime.continuous_batching_service import export_continuous_batching_manifest
from src.inference_runtime.inference_cost_governance_service import compute_inference_cost_estimate
from src.inference_runtime.inference_validation_service import (
    validate_batching_metadata,
    validate_parallelism_config,
    validate_speculative_metadata,
    validate_token_budget_category,
    validate_telemetry_structure,
    validate_uncontrolled_runtime_expansion_flag,
)
from src.inference_runtime.kv_cache_registry import export_kv_cache_registry_manifest
from src.inference_runtime.runtime_collapse_detection_service import assess_runtime_collapse_risk
from src.inference_runtime.runtime_efficiency_service import compute_runtime_efficiency_score
from src.inference_runtime.runtime_parallelism_service import evaluate_parallelism_gate
from src.inference_runtime.runtime_telemetry_service import export_runtime_telemetry_manifest
from src.inference_runtime.runtime_token_budget_service import categorize_budget
from src.inference_runtime.speculative_execution_service import export_speculative_execution_manifest

os.environ.setdefault("JWT_SECRET", "test-h041-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h041-inference-key"

app = create_app()
client = TestClient(app)

INF = "/api/v1/system/inference"


def test_valid_token_budget_accepted():
    validate_token_budget_category("orchestration")
    validate_token_budget_category("ensemble_evaluation")
    categorize_budget("retrieval")
    categorize_budget("ensemble_evaluation")


def test_invalid_budget_rejected():
    with pytest.raises(ValueError, match="invalid token budget"):
        validate_token_budget_category("unknown_budget_cat")


def test_batching_metadata_deterministic():
    a = json.dumps(export_continuous_batching_manifest(), sort_keys=True)
    b = json.dumps(export_continuous_batching_manifest(), sort_keys=True)
    assert a == b


def test_parallelism_governance_deterministic():
    a = evaluate_parallelism_gate(active_workflows=2, in_flight_tokens=10000, active_retries=0)
    b = evaluate_parallelism_gate(active_workflows=2, in_flight_tokens=10000, active_retries=0)
    assert a == b
    blocked = evaluate_parallelism_gate(active_workflows=99, in_flight_tokens=10000, active_retries=0)
    assert blocked["allowed"] is False


def test_unsafe_speculative_metadata_rejected():
    with pytest.raises(ValueError, match="unsafe speculative"):
        validate_speculative_metadata({"uncontrolled_speculative_execution": True})


def test_runtime_cost_calculation_deterministic():
    a = compute_inference_cost_estimate(input_tokens=1000, output_tokens=500)
    b = compute_inference_cost_estimate(input_tokens=1000, output_tokens=500)
    assert a == b
    with pytest.raises(ValueError):
        compute_inference_cost_estimate(input_tokens=-1, output_tokens=0)


def test_kv_metadata_deterministic():
    a = json.dumps(export_kv_cache_registry_manifest(), sort_keys=True)
    b = json.dumps(export_kv_cache_registry_manifest(), sort_keys=True)
    assert a == b


def test_runtime_telemetry_deterministic():
    man = export_runtime_telemetry_manifest()
    validate_telemetry_structure(man["sample_snapshot"])
    dup = export_runtime_telemetry_manifest()
    assert dup == man


def test_token_explosion_detected():
    snap = assess_runtime_collapse_risk(
        {"token_input_recent": 200000, "workflow_step_count": 2, "retry_count_windowed": 0, "orchestration_depth": 2}
    )
    assert "token_explosions" in snap["flags"]


def test_retry_storm_detected():
    snap = assess_runtime_collapse_risk(
        {
            "token_input_recent": 100,
            "workflow_step_count": 2,
            "retry_count_windowed": 20,
            "orchestration_depth": 2,
            "active_parallelism": 1,
            "orchestration_invoke_rps": 1.0,
        }
    )
    assert "retry_storms" in snap["flags"]


def test_prefill_pressure_classified():
    from src.inference_runtime.prefill_pressure_service import classify_prefill_pressure

    low = classify_prefill_pressure(
        {"context_tokens": 4000, "prefill_repeat_count": 1, "duplicate_context_chunks": 0, "retrieval_documents": 4}
    )
    assert low["pressure_level"] == "low"
    high = classify_prefill_pressure(
        {
            "context_tokens": 50000,
            "prefill_repeat_count": 6,
            "duplicate_context_chunks": 10,
            "retrieval_documents": 30,
        }
    )
    assert high["pressure_level"] in ("high", "critical")


def test_runtime_efficiency_score_deterministic():
    m = {
        "token_efficiency": 0.7,
        "latency_efficiency": 0.7,
        "orchestration_efficiency": 0.7,
        "batching_utilization": 0.7,
        "reflection_efficiency": 0.7,
        "retrieval_efficiency": 0.7,
    }
    a = compute_runtime_efficiency_score(m)
    b = compute_runtime_efficiency_score(m)
    assert a == b
    assert a["runtime_efficiency_score"] == 0.7


def test_speculative_manifest_safe():
    sm = export_speculative_execution_manifest()
    validate_speculative_metadata(sm)


def test_validation_helpers():
    validate_batching_metadata({"workflow_group_id": "wg_x", "batching_eligible": True})
    with pytest.raises(ValueError):
        validate_batching_metadata({"workflow_group_id": "wg_x"})
    validate_parallelism_config(
        {"max_parallel_workflows": 4, "token_concurrency_cap": 10000, "max_retry_concurrency": 2}
    )
    with pytest.raises(ValueError):
        validate_uncontrolled_runtime_expansion_flag({"uncontrolled_runtime_expansion": True})


def test_api_inference_envelope():
    r = client.get(f"{INF}/token-budgets")
    assert r.status_code == 200
    body = r.json()
    assert body["uncontrolled_runtime_expansion"] is False
    assert body["token_budgets"]["overflow_handling_explicit"] is True
    assert body["token_budgets"]["ensemble_aware_budgeting"] is True
