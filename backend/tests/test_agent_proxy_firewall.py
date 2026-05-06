"""
TEST: agent_proxy_firewall (H-039)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from src.agent_proxy_firewall.compression_resilience_service import export_compression_resilience_manifest
from src.agent_proxy_firewall.firewall_validation_service import validate_unsafe_firewall_flags
from src.agent_proxy_firewall.input_filter_chain_service import assess_input_payload, validate_input_filter_id
from src.agent_proxy_firewall.output_filter_chain_service import assess_output_payload
from src.agent_proxy_firewall.policy_interceptor_service import export_policy_interception_manifest
from src.agent_proxy_firewall.sensitive_action_guard_service import assess_sensitive_action
from src.agent_proxy_firewall.trace_interception_service import export_interception_traces
from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h039-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h039-firewall-key"

app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/firewall"


def test_valid_input_filter_accepted():
    validate_input_filter_id("prompt_injection_scan")
    r = assess_input_payload("Normal procurement summary for Q2.")
    assert r["allowed"] is True


def test_dangerous_outputs_blocked():
    r = assess_output_payload("Suggested shell: rm -rf /")
    assert r["blocked"] is True


def test_protected_actions_intercepted():
    r = assess_sensitive_action("mass_delete", human_approval_present=False)
    assert r["intercepted"] is True


def test_compression_resilient_enforcement_deterministic():
    a = json.dumps(export_compression_resilience_manifest(), sort_keys=True)
    b = json.dumps(export_compression_resilience_manifest(), sort_keys=True)
    assert a == b


def test_unsafe_execution_rejected():
    with pytest.raises(ValueError):
        validate_unsafe_firewall_flags({"unrestricted_autonomous_execution": True})


def test_interception_traces_deterministic():
    a = json.dumps(export_interception_traces(), sort_keys=True)
    b = json.dumps(export_interception_traces(), sort_keys=True)
    assert a == b


def test_policy_enforcement_deterministic():
    a = json.dumps(export_policy_interception_manifest(), sort_keys=True)
    b = json.dumps(export_policy_interception_manifest(), sort_keys=True)
    assert a == b


def test_api_gateways_envelope():
    r = client.get(f"{BASE}/gateways")
    assert r.status_code == 200
    body = r.json()
    assert body.get("direct_agent_provider_trust") is False
    assert "compression_resilience" in body
    align = body.get("runtime_inference_alignment") or {}
    assert align.get("detection_only") is True
    assert align.get("h041_inference_runtime_alignment") is True
    assert align.get("h043_private_runtime_exposure_alignment") is True


def test_api_policies_include_execution_firewall():
    r = client.get(f"{BASE}/policies")
    assert r.status_code == 200
    pol = r.json()["policies"]
    assert "execution_firewall" in pol
    assert pol["execution_firewall"]["unrestricted_autonomous_execution"] is False
