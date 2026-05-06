"""
TEST: trajectory_evaluation (H-028)
PURPOSE: Registry, grouping, deterministic scoring, traces
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.trajectory_evaluation.comparison_reasoning_service import build_evaluation_narrative
from src.trajectory_evaluation.relative_scoring_service import rank_trajectories
from src.trajectory_evaluation.trajectory_registry import (
    create_trajectory,
    get_trajectory_store,
    reset_trajectory_store_for_tests,
)
from src.trajectory_evaluation.trajectory_schema import TrajectoryCreateRequest

os.environ.setdefault("JWT_SECRET", "test-h028-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h028-trajectory-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/trajectory"


@pytest.fixture(autouse=True)
def _reset_store():
    reset_trajectory_store_for_tests()
    yield
    reset_trajectory_store_for_tests()


def _mk_body(suffix: str, **meta):
    return {
        "workflow_name": "opportunity_rank",
        "strategy_name": "json_prompting",
        "input_summary": f"input {suffix}",
        "output_summary": f"output {suffix}",
        "reasoning_metadata": meta,
        "tags": ["test"],
    }


def test_valid_trajectory_accepted():
    r = client.post(BASE, json=_mk_body("a", commercial_usefulness=0.9))
    assert r.status_code == 200
    body = r.json()
    assert body.get("deterministic_trajectory_evaluation") is True
    assert body.get("hidden_reasoning_exposure") == "none"
    assert "trajectory_id" in body["trajectory"]


def test_valid_group_accepted():
    a = client.post(BASE, json=_mk_body("g1", geographic_relevance=0.8)).json()["trajectory"]["trajectory_id"]
    b = client.post(BASE, json=_mk_body("g2", geographic_relevance=0.4)).json()["trajectory"]["trajectory_id"]
    r = client.post(
        f"{BASE}/group",
        json={
            "workflow_name": "opportunity_rank",
            "shared_input_summary": "same tender",
            "trajectory_ids": [a, b],
            "comparison_notes": "fixture",
        },
    )
    assert r.status_code == 200
    assert r.json()["group"]["group_id"]


def test_invalid_group_rejected():
    a = client.post(BASE, json=_mk_body("x1")).json()["trajectory"]["trajectory_id"]
    b_body = _mk_body("x2")
    b_body["workflow_name"] = "other_flow"
    b = client.post(BASE, json=b_body).json()["trajectory"]["trajectory_id"]
    r = client.post(
        f"{BASE}/group",
        json={
            "workflow_name": "opportunity_rank",
            "shared_input_summary": "mixed",
            "trajectory_ids": [a, b],
        },
    )
    assert r.status_code == 422


def test_relative_scoring_deterministic():
    store = get_trajectory_store()
    t1 = create_trajectory(
        store,
        TrajectoryCreateRequest(**_mk_body("r1", commercial_usefulness=0.9, hallucination_risk=0.1)),
    )
    t2 = create_trajectory(
        store,
        TrajectoryCreateRequest(**_mk_body("r2", commercial_usefulness=0.4, hallucination_risk=0.8)),
    )
    r1, _ = rank_trajectories([t1, t2])
    r2, _ = rank_trajectories([t1, t2])
    assert r1 == r2
    assert r1[0] == t1.trajectory_id


def test_comparison_reasoning_deterministic():
    store = get_trajectory_store()
    t1 = create_trajectory(store, TrajectoryCreateRequest(**_mk_body("c1", structured_output_quality=0.95)))
    t2 = create_trajectory(store, TrajectoryCreateRequest(**_mk_body("c2", structured_output_quality=0.3)))
    ranked, meta = rank_trajectories([t1, t2])
    n1 = build_evaluation_narrative(ranked, meta)
    n2 = build_evaluation_narrative(ranked, meta)
    assert n1 == n2


def test_evaluation_traces_stored():
    a = client.post(BASE, json=_mk_body("e1", graph_consistency=0.9)).json()["trajectory"]["trajectory_id"]
    b = client.post(BASE, json=_mk_body("e2", graph_consistency=0.2)).json()["trajectory"]["trajectory_id"]
    g = client.post(
        f"{BASE}/group",
        json={
            "workflow_name": "opportunity_rank",
            "shared_input_summary": "graph eval",
            "trajectory_ids": [a, b],
        },
    ).json()["group"]["group_id"]
    ev = client.post(f"{BASE}/evaluate", json={"group_id": g})
    assert ev.status_code == 200
    lst = client.get(f"{BASE}/evaluations")
    assert lst.status_code == 200
    assert len(lst.json()["evaluations"]) >= 1


def test_invalid_evaluation_rejected():
    r = client.post(f"{BASE}/evaluate", json={"group_id": "grp_nonexistent"})
    assert r.status_code == 422


def test_get_groups_list():
    client.post(BASE, json=_mk_body("l1"))
    r = client.get(f"{BASE}/groups")
    assert r.status_code == 200
    assert isinstance(r.json()["groups"], list)


def test_envelope_flags():
    r = client.get(f"{BASE}/groups")
    assert r.json().get("reinforcement_learning_training") is False
