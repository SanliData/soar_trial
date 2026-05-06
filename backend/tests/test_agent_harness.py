"""
TEST: agent_harness (H-031)
PURPOSE: Registries, compression, boundaries, runtime summary
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.agent_harness.compression_service import summarize_context
from src.agent_harness.evaluation_router import route_evaluation
from src.agent_harness.harness_runtime_service import generate_runtime_summary
from src.agent_harness.memory_registry import MEMORY_TYPES
from src.agent_harness.protocol_registry import PROTOCOL_REGISTRY
from src.agent_harness.skill_registry import SKILL_REGISTRY
from src.agent_harness.harness_validation_service import validate_memory_type
from src.agent_harness.subagent_boundary_service import (
    MAX_SUBAGENTS_PER_SESSION,
    validate_subagent_spawn,
)

os.environ.setdefault("JWT_SECRET", "test-h031-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h031-harness-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/harness"


def test_valid_memory_domain_accepted():
    assert "working_memory" in MEMORY_TYPES
    validate_memory_type("semantic_memory")


def test_invalid_memory_type_rejected():
    with pytest.raises(ValueError, match="invalid memory_type"):
        validate_memory_type("volatile_ram")


def test_skill_registry_deterministic():
    a = json.dumps(sorted(SKILL_REGISTRY.keys()))
    b = json.dumps(sorted(SKILL_REGISTRY.keys()))
    assert a == b


def test_protocol_registry_deterministic():
    a = json.dumps(sorted(PROTOCOL_REGISTRY.keys()))
    b = json.dumps(sorted(PROTOCOL_REGISTRY.keys()))
    assert a == b


def test_compression_deterministic():
    t = "x" * 9000
    a = summarize_context(t, max_chars=400)
    b = summarize_context(t, max_chars=400)
    assert a == b


def test_subagent_boundary_enforced():
    validate_subagent_spawn(0, "read_only", ["read:graph"])
    with pytest.raises(ValueError, match="spawn limit"):
        validate_subagent_spawn(MAX_SUBAGENTS_PER_SESSION, "read_only", ["read:graph"])
    with pytest.raises(ValueError, match="scope not allowed"):
        validate_subagent_spawn(0, "unknown_scope", ["read:graph"])


def test_runtime_summary_deterministic():
    s1 = generate_runtime_summary()
    s2 = generate_runtime_summary()
    assert s1 == s2


def test_evaluation_routing():
    r = route_evaluation("graph")
    assert r["evaluation_target"] == "graph_evaluation"


def test_api_memory_envelope():
    r = client.get(f"{BASE}/memory")
    assert r.status_code == 200
    assert r.json().get("recursive_agent_swarm") is False


def test_api_compress_context():
    r = client.post(
        f"{BASE}/compress",
        json={"mode": "context", "payload": "hello " * 900},
    )
    assert r.status_code == 200
    assert r.json()["compression"]["kind"] == "context"


def test_api_compress_invalid_memory_type():
    r = client.post(
        f"{BASE}/compress",
        json={"mode": "memory", "payload": "x", "memory_type": "bad_ram"},
    )
    assert r.status_code == 422
