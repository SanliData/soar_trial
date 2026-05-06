"""
TEST: ai_runtime (H-021)
PURPOSE: Deterministic budgeting and routing without LLM calls
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h021-jwt-secret-32characters!!")
os.environ["SOARB2B_API_KEYS"] = "test-h021-api-key"

from src.ai_runtime.model_routing_service import route_model
from src.ai_runtime.prompt_compaction_service import compact_context
from src.ai_runtime.runtime_schema import AIRuntimeTask
from src.ai_runtime.runtime_telemetry_service import clear_profiles_for_tests
from src.ai_runtime.token_budget_service import enforce_token_budget, estimate_tokens

clear_profiles_for_tests()
app = create_app()
client = TestClient(app)

PROFILE_PATH = "/api/v1/system/ai-runtime/profile"
LIST_PATH = "/api/v1/system/ai-runtime/profiles"


@pytest.fixture(autouse=True)
def _reset_telemetry():
    clear_profiles_for_tests()
    yield


def test_estimate_tokens_positive():
    assert estimate_tokens("abcd") >= 1


def test_token_budget_truncates():
    long_text = "word " * 5000
    res = enforce_token_budget(long_text, max_tokens=50)
    assert res.truncated is True
    assert estimate_tokens(res.text) <= 50


def test_compaction_applies_marker():
    blob = "SECTION_HEAD " * 200 + "TAIL " * 200
    out = compact_context(blob, max_tokens=80)
    assert out.compaction_applied is True
    assert "[Context compacted deterministically]" in out.compacted_text


def test_model_routing_special_cases():
    r1 = route_model(
        AIRuntimeTask(
            task_id="t1",
            task_type="graph_reasoning",
            requested_quality_tier="premium",
            max_input_tokens=8000,
            max_output_tokens=500,
            latency_target_ms=4000,
            allow_compaction=True,
            preferred_model=None,
        )
    )
    assert r1["selected_model"] == "premium-reasoner"

    r2 = route_model(
        AIRuntimeTask(
            task_id="t2",
            task_type="generative_ui_widget",
            requested_quality_tier="standard",
            max_input_tokens=2000,
            max_output_tokens=400,
            latency_target_ms=2500,
            allow_compaction=True,
            preferred_model=None,
        )
    )
    assert r2["selected_model"] == "standard-reasoner"

    r3 = route_model(
        AIRuntimeTask(
            task_id="t3",
            task_type="analytics_summary",
            requested_quality_tier="economy",
            max_input_tokens=1500,
            max_output_tokens=200,
            latency_target_ms=3000,
            allow_compaction=False,
            preferred_model=None,
        )
    )
    assert r3["selected_model"] == "economy-reasoner"


def test_build_profile_via_api_has_llm_invoked_false():
    payload = {
        "task": {
            "task_id": "pytest-h021",
            "task_type": "executive_briefing",
            "requested_quality_tier": "standard",
            "max_input_tokens": 400,
            "max_output_tokens": 200,
            "latency_target_ms": 5000,
            "allow_compaction": True,
            "preferred_model": None,
        },
        "input_context": "Short context for deterministic sizing.",
    }
    r = client.post(PROFILE_PATH, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["llm_invoked"] is False
    assert body["profile"]["selected_model"] == "standard-reasoner"


def test_invalid_task_type_rejected():
    payload = {
        "task": {
            "task_id": "bad",
            "task_type": "unknown_task",
            "requested_quality_tier": "standard",
            "max_input_tokens": 100,
            "max_output_tokens": 50,
            "latency_target_ms": 1000,
            "allow_compaction": True,
            "preferred_model": None,
        },
        "input_context": "",
    }
    r = client.post(PROFILE_PATH, json=payload)
    assert r.status_code == 422


def test_invalid_quality_tier_rejected():
    payload = {
        "task": {
            "task_id": "bad",
            "task_type": "executive_briefing",
            "requested_quality_tier": "luxury",
            "max_input_tokens": 100,
            "max_output_tokens": 50,
            "latency_target_ms": 1000,
            "allow_compaction": True,
            "preferred_model": None,
        },
        "input_context": "",
    }
    r = client.post(PROFILE_PATH, json=payload)
    assert r.status_code == 422


def test_profiles_endpoint_lists_recent():
    client.post(
        PROFILE_PATH,
        json={
            "task": {
                "task_id": "list-me",
                "task_type": "market_signal_summary",
                "requested_quality_tier": "economy",
                "max_input_tokens": 300,
                "max_output_tokens": 150,
                "latency_target_ms": 2000,
                "allow_compaction": True,
                "preferred_model": None,
            },
            "input_context": "signal context",
        },
    )
    r = client.get(LIST_PATH)
    assert r.status_code == 200
    data = r.json()
    assert data["llm_invoked"] is False
    assert len(data["profiles"]) >= 1
