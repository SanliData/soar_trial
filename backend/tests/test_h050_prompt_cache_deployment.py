"""
TEST: test_h050_prompt_cache_deployment
PURPOSE: Determinism + governance checks for H-050 foundation
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import pytest

from src.agent_deployment_profiles.deployment_profile_registry import export_deployment_profiles
from src.agent_deployment_profiles.deployment_profile_validation import reject_unrestricted_public_deployment
from src.agent_deployment_profiles.deployment_safety_service import export_deployment_safety
from src.prompt_cache_governance.static_prefix_registry import export_static_prefix_registry
from src.prompt_cache_governance.dynamic_suffix_service import export_dynamic_suffix
from src.prompt_cache_governance.cache_efficiency_service import compute_cache_efficiency
from src.prompt_cache_governance.tool_schema_stability_service import export_tool_schema_stability
from src.prompt_cache_governance.model_session_stability_service import export_model_session_stability
from src.prompt_cache_governance.cache_safe_compression_service import export_cache_safe_compression
from src.prompt_cache_governance.prompt_cache_validation_service import detect_volatile_content


def test_static_prefix_deterministic():
    a = export_static_prefix_registry()
    b = export_static_prefix_registry()
    assert a == b
    assert a["static_prefix_stable"] is True
    assert all(c["cacheable"] is True for c in a["static_prefix_components"])


def test_volatile_prefix_content_rejected_by_detector():
    assert detect_volatile_content("timestamp=2026-05-06") is True
    assert detect_volatile_content("uuid=123e4567-e89b-12d3-a456-426614174000") is True
    assert detect_volatile_content("system_rules:finderos_governed_foundation_v1") is False


def test_dynamic_suffix_does_not_mutate_prefix():
    p1 = export_static_prefix_registry()
    s = export_dynamic_suffix(session_id="sess-demo-001")
    p2 = export_static_prefix_registry()
    assert p1 == p2
    assert s["static_prefix_mutated"] is False


def test_cache_efficiency_deterministic_and_div0_safe():
    m = compute_cache_efficiency(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=0)
    assert m["cache_efficiency_ratio"] == 0.0
    m2 = compute_cache_efficiency(cache_creation_input_tokens=8000, cache_read_input_tokens=12000, input_tokens=15000)
    assert 0.0 <= m2["cache_efficiency_ratio"] <= 1.0


def test_tool_schema_stability_detection_surface():
    st = export_tool_schema_stability(session_id="sess-demo-001")
    assert st["detection_only"] is True
    assert "tool_schema_fingerprint" in st
    assert st["cache_reset_warning"] is False


def test_model_session_stability_surface():
    ms = export_model_session_stability(session_id="sess-demo-001")
    assert ms["model_switch_requires_reset"] is True
    assert ms["explicit_reset_metadata_required"] is True


def test_cache_safe_compression_preserves_prefix():
    c = export_cache_safe_compression(session_id="sess-demo-001")
    assert c["static_prefix_preserved"] is True
    assert c["compression_instruction_added_as_suffix"] is True


def test_unsafe_public_deployment_profile_rejected():
    bad = {
        "profile_id": "bad_public",
        "runtime_visibility": "public",
        "public_unrestricted_default": True,
        "allowed_channels": ["slack"],
        "identity_required": False,
        "firewall_required": False,
    }
    with pytest.raises(ValueError):
        reject_unrestricted_public_deployment(bad)


def test_deployment_safety_risk_deterministic():
    a = export_deployment_safety()
    b = export_deployment_safety()
    assert a == b
    rows = a["deployment_safety"]
    assert rows and all("risk_level" in r for r in rows)


def test_deployment_profiles_no_public_defaults():
    profiles = export_deployment_profiles()["deployment_profiles"]
    assert profiles
    assert all(p["runtime_visibility"] != "public" for p in profiles)
    assert all(p["public_unrestricted_default"] is False for p in profiles)

