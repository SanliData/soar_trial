"""
TEST: semantic_capabilities (H-020)
PURPOSE: Deterministic registry + export semantics
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-sem-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-sem-capability-registry-key"

from src.semantic_capabilities.capability_schema import CapabilityDefinition
from src.semantic_capabilities.capability_export_service import build_capabilities_catalog
from src.semantic_capabilities.capability_loader import (
    invalidate_capability_cache_for_tests,
    load_capabilities,
)
from src.semantic_capabilities.capability_validation import validate_capability_definitions

invalidate_capability_cache_for_tests()
app = create_app()
client = TestClient(app)


def _base_kwargs(**kw: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "capability_id": "fixture.sample",
        "name": "Sample",
        "domain": "fixtures",
        "description": "Synthetic capability fixture for validators.",
        "endpoint": "/v1/example",
        "http_method": "GET",
        "auth_required": False,
        "idempotent": True,
        "rate_limit": "none_fixture",
        "risk_level": "low",
        "sensitive_fields": [],
        "destructive_action": False,
        "orchestration_safe": True,
        "human_approval_required": False,
        "allowed_roles": [],
        "input_schema_summary": "none",
        "output_schema_summary": "none",
        "tags": ["fixture"],
    }
    data.update(kw)
    return data


def test_registry_loads_successfully():
    caps = load_capabilities()
    assert len(caps) == 129


def test_all_capabilities_validate():
    validate_capability_definitions(list(load_capabilities()))


def test_invalid_risk_level_rejected():
    with pytest.raises(ValidationError):
        CapabilityDefinition(**_base_kwargs(risk_level="extreme"))  ***REMOVED*** type: ignore[arg-type]


def test_duplicate_capability_id_rejected():
    sample = CapabilityDefinition(**_base_kwargs(capability_id="dup.test"))
    with pytest.raises(ValueError, match="duplicate capability_id"):
        validate_capability_definitions([sample, sample])


def test_export_payload_deterministic():
    first = build_capabilities_catalog()
    second = build_capabilities_catalog()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_export_endpoint_returns_json():
    invalidate_capability_cache_for_tests()
    resp = client.get("/api/v1/system/capabilities")
    assert resp.status_code == 200
    body = resp.json()
    assert body["system"] == "FinderOS / SOAR B2B"
    assert isinstance(body.get("capabilities"), list)
    assert len(body["capabilities"]) == 129
    assert body.get("semantic_capability_graph", {}).get("schema_version") == "h034_v1"
    lowered = json.dumps(body).lower()
    assert "<script" not in lowered  ***REMOVED*** gratuitous XSS guard regression


def test_orchestration_metadata_present_on_each_row():
    resp = client.get("/api/v1/system/capabilities")
    payload = resp.json()
    meta_keys = {"orchestration_safe", "destructive_action", "human_approval_required"}
    for row in payload["capabilities"]:
        assert meta_keys <= row.keys()


def test_destructive_action_validation_rules():
    bad = CapabilityDefinition(
        **_base_kwargs(
            capability_id="regression.bad_destructive",
            destructive_action=True,
            human_approval_required=False,
            orchestration_safe=False,
        )
    )
    with pytest.raises(ValueError, match="human_approval_required"):
        validate_capability_definitions([bad])


def test_destructive_forbids_orchestration_safe():
    bad = CapabilityDefinition(
        **_base_kwargs(
            capability_id="regression.bad_orch_safe",
            destructive_action=True,
            human_approval_required=True,
            orchestration_safe=True,
        )
    )
    with pytest.raises(ValueError, match="orchestration_safe"):
        validate_capability_definitions([bad])


def test_human_approval_enforced_for_export_like_flows():
    approval_ids = {
        "exposure.create",
        "onboarding.create_plan",
        "route_export.create_visit_route",
        "security.risk_score",
    }
    for row in load_capabilities():
        assert row.capability_id is not None
        if row.capability_id in approval_ids:
            assert row.human_approval_required is True
