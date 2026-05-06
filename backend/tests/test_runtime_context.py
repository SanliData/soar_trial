"""
TEST: runtime_context (H-030)
PURPOSE: Metadata, topology, budgeting, hints
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.app import create_app
from src.runtime_context.backend_metadata_service import build_backend_metadata_snapshot
from src.runtime_context.capability_snapshot_service import build_capability_snapshots
from src.runtime_context.context_budget_service import apply_context_budget, prioritize_context
from src.runtime_context.context_trace_service import reset_context_trace_store_for_tests
from src.runtime_context.orchestration_context_service import build_runtime_bundle
from src.runtime_context.runtime_context_validation_service import (
    MAX_LARGE_TEXT_CHARS,
    ContextBudgetRequest,
)
from src.runtime_context.runtime_hint_service import build_runtime_hints
from src.runtime_context.runtime_topology_service import build_topology_snapshot

os.environ.setdefault("JWT_SECRET", "test-h030-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h030-runtime-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/runtime"


@pytest.fixture(autouse=True)
def _reset_trace():
    reset_context_trace_store_for_tests()
    yield
    reset_context_trace_store_for_tests()


def test_metadata_snapshot_valid():
    s = build_backend_metadata_snapshot()
    assert "active_modules" in s and "enabled_capabilities" in s
    assert s["graph_status"] == "available"
    assert "progressive_context" in s


def test_capability_snapshot_valid():
    snap = build_capability_snapshots("summary")
    assert snap["count"] >= 1
    assert snap["capabilities"][0]["capability_name"]


def test_topology_deterministic():
    a = build_topology_snapshot()
    b = build_topology_snapshot()
    assert a == b


def test_context_budgeting_deterministic():
    r1 = apply_context_budget(1200, ["metadata", "capabilities", "topology"], "")
    r2 = apply_context_budget(1200, ["metadata", "capabilities", "topology"], "")
    assert r1["budget_digest"] == r2["budget_digest"]


def test_progressive_loading_depth():
    summary = build_capability_snapshots("summary")
    full = build_capability_snapshots("full")
    assert "endpoint" not in summary["capabilities"][0]
    assert "endpoint" in full["capabilities"][0]


def test_oversized_payload_rejected():
    with pytest.raises(ValidationError):
        ContextBudgetRequest(large_text_sample="x" * (MAX_LARGE_TEXT_CHARS + 1))


def test_orchestration_hints_deterministic():
    bundle = build_runtime_bundle()
    h1 = build_runtime_hints(bundle)
    h2 = build_runtime_hints(bundle)
    assert h1 == h2


def test_prioritize_within_budget():
    p = prioritize_context(["metadata", "capabilities", "topology", "full_capability_payload"], 500.0)
    assert "metadata" in p["included_layers"]


def test_api_metadata_envelope():
    r = client.get(f"{BASE}/metadata")
    assert r.status_code == 200
    assert r.json().get("runtime_self_modification") is False


def test_api_capabilities_invalid_depth():
    r = client.get(f"{BASE}/capabilities?depth=evil")
    assert r.status_code == 422


def test_api_context_budget():
    r = client.post(
        f"{BASE}/context-budget",
        json={"estimated_chars": 800, "requested_layers": ["metadata", "hints"], "large_text_sample": ""},
    )
    assert r.status_code == 200
    assert "budget" in r.json()
