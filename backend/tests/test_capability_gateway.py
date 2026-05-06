"""
TEST: capability_gateway (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.capability_gateway.external_tool_governance_service import export_external_tool_governance
from src.capability_gateway.gateway_validation_service import (
    validate_execution_scope,
    validate_gateway_name,
    validate_unsafe_execution_flags,
)
from src.capability_gateway.hybrid_serving_service import export_hybrid_serving_metadata
from src.capability_gateway.mcp_gateway_registry import GATEWAYS
from src.capability_gateway.provider_abstraction_service import select_provider

os.environ.setdefault("JWT_SECRET", "test-h037-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h037-gateway-key"

app = create_app()
client = TestClient(app)


def test_valid_gateway_accepted():
    validate_gateway_name("browser_intelligence")
    assert "gis_enrichment" in GATEWAYS


def test_invalid_gateway_rejected():
    with pytest.raises(ValueError, match="invalid gateway name"):
        validate_gateway_name("unknown_gateway")


def test_provider_abstraction_deterministic():
    a = json.dumps(select_provider("privacy_strict"), sort_keys=True)
    b = json.dumps(select_provider("privacy_strict"), sort_keys=True)
    assert a == b


def test_browser_policies_enforced():
    r = client.get("/api/v1/system/browser-policies")
    assert r.status_code == 200
    body = r.json()
    assert body["browser_policies"]["unrestricted_browser_automation"] is False


def test_execution_scopes_deterministic():
    validate_execution_scope("sandboxed_dom")
    with pytest.raises(ValueError):
        validate_execution_scope("arbitrary_internet")


def test_unsafe_execution_rejected():
    with pytest.raises(ValueError):
        validate_unsafe_execution_flags({"unrestricted_external_execution": True})


def test_hybrid_serving_abstraction_deterministic():
    a = json.dumps(export_hybrid_serving_metadata(), sort_keys=True)
    b = json.dumps(export_hybrid_serving_metadata(), sort_keys=True)
    assert a == b


def test_external_tool_governance_no_unrestricted_chaining():
    g = export_external_tool_governance()
    assert g["unrestricted_tool_chaining"] is False


def test_api_gateways_envelope():
    r = client.get("/api/v1/system/gateways")
    assert r.status_code == 200
    body = r.json()
    assert body.get("unrestricted_external_execution") is False
    assert len(body["gateways"]) >= 5
