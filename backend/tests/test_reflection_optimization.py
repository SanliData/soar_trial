"""
TEST: reflection_optimization (H-022)
PURPOSE: Deterministic reflection traces and human-gated candidates
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h022-jwt-secret-32characters!!")
os.environ["SOARB2B_API_KEYS"] = "test-h022-api-key"

from src.reflection_optimization.optimization_history_service import clear_history_for_tests
from src.reflection_optimization.prompt_candidate_registry import clear_candidates_for_tests
from src.reflection_optimization.prompt_revision_service import build_candidate_from_trace
from src.reflection_optimization.reflection_schema import ReflectionTrace
from src.reflection_optimization.reflection_trace_service import clear_traces_for_tests

clear_traces_for_tests()
clear_candidates_for_tests()
clear_history_for_tests()

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/reflection"


@pytest.fixture(autouse=True)
def _reset_stores():
    clear_traces_for_tests()
    clear_candidates_for_tests()
    clear_history_for_tests()
    yield


def test_trace_creation_works():
    body = {
        "task_type": "executive_briefing",
        "workflow_name": "results_hub.briefing.v1",
        "input_summary": "plan-123",
        "output_summary": "generic summary",
        "success": False,
        "score": 0.3,
        "failure_modes": ["overly_generic_executive_summary"],
        "execution_notes": "deterministic test trace",
    }
    r = client.post(f"{BASE}/trace", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["autonomous_execution"] is False
    assert data["trace"]["trace_id"]


def test_candidate_creation_defaults():
    t = client.post(
        f"{BASE}/trace",
        json={
            "task_type": "graph_reasoning",
            "workflow_name": "graph.reason.v1",
            "success": False,
            "score": 0.2,
            "failure_modes": ["low_confidence_graph_edge"],
        },
    ).json()["trace"]
    r = client.post(f"{BASE}/candidate", json={"trace_id": t["trace_id"]})
    assert r.status_code == 200
    data = r.json()
    assert data["autonomous_execution"] is False
    c = data["candidate"]
    assert c["approval_status"] == "pending"
    assert c["human_review_required"] is True


def test_invalid_task_type_rejected():
    r = client.post(
        f"{BASE}/trace",
        json={
            "task_type": "unknown_task",
            "workflow_name": "wf",
            "success": True,
            "score": 1.0,
        },
    )
    assert r.status_code == 422


def test_failure_modes_required_when_not_successful():
    r = client.post(
        f"{BASE}/trace",
        json={
            "task_type": "executive_briefing",
            "workflow_name": "wf",
            "success": False,
            "score": 0.0,
            "failure_modes": [],
        },
    )
    assert r.status_code == 422


def test_deterministic_revision_generation():
    trace = ReflectionTrace(
        trace_id="fixed-id",
        task_type="market_signal_summary",
        workflow_name="signals.v1",
        success=False,
        score=0.4,
        failure_modes=["poor_signal_prioritization"],
        created_at=datetime.utcnow(),
    )
    cand = build_candidate_from_trace(trace)
    assert "prioritization" in cand.proposed_prompt_summary.lower()


def test_approve_requires_explicit_action():
    t = client.post(
        f"{BASE}/trace",
        json={
            "task_type": "opportunity_ranking",
            "workflow_name": "opp.rank.v1",
            "success": False,
            "score": 0.5,
            "failure_modes": ["repeated_opportunity_cluster"],
        },
    ).json()["trace"]
    cid = client.post(f"{BASE}/candidate", json={"trace_id": t["trace_id"]}).json()["candidate"]["candidate_id"]

    r_ok = client.post(
        f"{BASE}/candidate/{cid}/approve",
        json={"approved_by": "reviewer@example.com", "evaluation_notes": "ok"},
    )
    assert r_ok.status_code == 200
    assert r_ok.json()["autonomous_execution"] is False
    assert r_ok.json()["candidate"]["approval_status"] == "approved"

    r_twice = client.post(
        f"{BASE}/candidate/{cid}/approve",
        json={"approved_by": "reviewer@example.com"},
    )
    assert r_twice.status_code == 422


def test_reject_workflow():
    t = client.post(
        f"{BASE}/trace",
        json={
            "task_type": "generative_ui_widget",
            "workflow_name": "genui.v1",
            "success": False,
            "score": 0.1,
            "failure_modes": ["missing_market_context"],
        },
    ).json()["trace"]
    cid = client.post(f"{BASE}/candidate", json={"trace_id": t["trace_id"]}).json()["candidate"]["candidate_id"]
    r = client.post(
        f"{BASE}/candidate/{cid}/reject",
        json={"rejected_by": "audit@example.com", "evaluation_notes": "no"},
    )
    assert r.status_code == 200
    assert r.json()["candidate"]["approval_status"] == "rejected"
    assert r.json()["autonomous_execution"] is False


def test_list_endpoints_include_guard_flag():
    r1 = client.get(f"{BASE}/traces")
    r2 = client.get(f"{BASE}/candidates")
    assert r1.json()["autonomous_execution"] is False
    assert r2.json()["autonomous_execution"] is False
