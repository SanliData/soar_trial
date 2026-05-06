"""
SCRIPT: verify_h050_prompt_cache_deployment
PURPOSE: Verification for H-050 prompt cache governance + deployment profiles
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


def _assert_exists(rel: str) -> None:
    p = ROOT / rel
    assert p.exists(), f"missing: {rel}"


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _assert_utf8_no_bom(rel: str) -> None:
    raw = (ROOT / rel).read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected: {rel}"


def _assert_no_secrets(rel: str) -> None:
    txt = _read(rel).lower()
    banned = ["api_key", "secret_key", "password=", "private_key", "sk-", "-----begin private key-----"]
    assert not any(b in txt for b in banned), f"potential secret marker in {rel}"


def _assert_router_thin(rel: str) -> None:
    txt = _read(rel)
    banned = ["compute_cache_efficiency(", "score_deployment_profile(", "hashlib.", "sha256("]
    assert not any(b in txt for b in banned), f"router contains business logic marker: {rel}"


def _optional_get(base: str, path: str) -> None:
    with urlopen(base.rstrip("/") + path) as r:
        assert 200 <= r.status < 300, f"GET failed: {path} status={r.status}"


def main() -> int:
    ***REMOVED*** Required files
    required = [
        "backend/src/prompt_cache_governance/__init__.py",
        "backend/src/prompt_cache_governance/static_prefix_registry.py",
        "backend/src/prompt_cache_governance/dynamic_suffix_service.py",
        "backend/src/prompt_cache_governance/cache_breakpoint_service.py",
        "backend/src/prompt_cache_governance/cache_efficiency_service.py",
        "backend/src/prompt_cache_governance/tool_schema_stability_service.py",
        "backend/src/prompt_cache_governance/model_session_stability_service.py",
        "backend/src/prompt_cache_governance/cache_safe_compression_service.py",
        "backend/src/prompt_cache_governance/prompt_cache_validation_service.py",
        "backend/src/agent_deployment_profiles/__init__.py",
        "backend/src/agent_deployment_profiles/deployment_profile_registry.py",
        "backend/src/agent_deployment_profiles/deployment_safety_service.py",
        "backend/src/http/v1/prompt_cache_governance_router.py",
        "backend/src/http/v1/agent_deployment_profiles_router.py",
        "backend/src/ui/en/prompt_cache_governance_demo.html",
        "backend/src/ui/tr/prompt_cache_governance_demo.html",
        "backend/src/ui/en/agent_deployment_profiles_demo.html",
        "backend/src/ui/tr/agent_deployment_profiles_demo.html",
        "docs/H-050_PROMPT_CACHE_DEPLOYMENT_PROFILES.md",
        "docs/H-050_IMPLEMENTATION_PROOF.md",
    ]
    for r in required:
        _assert_exists(r)
        _assert_utf8_no_bom(r)
        _assert_no_secrets(r)

    ***REMOVED*** Routers registered
    app_py = _read("backend/src/app.py")
    assert "prompt_cache_governance_router" in app_py, "router not registered: prompt_cache_governance_router"
    assert "agent_deployment_profiles_router" in app_py, "router not registered: agent_deployment_profiles_router"

    ***REMOVED*** Books/backlog updated
    mainbook = _read("backend/docs/main_book/FinderOS_MainBook_v0.1.html")
    livebook = _read("backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html")
    backlog = _read("docs/SOARB2B_MASTER_BACKLOG.md")
    assert "H-050 Prompt Cache Governance" in mainbook, "MainBook missing H-050 section"
    assert "H-050 Verification" in livebook, "LiveBook missing H-050 verification section"
    assert "***REMOVED******REMOVED*** H-050 — Prompt Cache Governance" in backlog, "Master backlog missing H-050 entry"

    ***REMOVED*** Thin routers
    _assert_router_thin("backend/src/http/v1/prompt_cache_governance_router.py")
    _assert_router_thin("backend/src/http/v1/agent_deployment_profiles_router.py")

    ***REMOVED*** No public unrestricted defaults (static check)
    profiles_py = _read("backend/src/agent_deployment_profiles/deployment_profile_registry.py").lower()
    assert "runtime_visibility\": \"public" not in profiles_py, "public runtime visibility found in registry"
    assert "public_unrestricted_default" in profiles_py, "missing explicit public_unrestricted_default control"

    ***REMOVED*** Optional HTTP checks
    base = os.environ.get("VERIFY_BASE_URL")
    if base:
        _optional_get(base, "/api/v1/system/cache/static-prefix")
        _optional_get(base, "/api/v1/system/cache/efficiency")
        _optional_get(base, "/api/v1/system/cache/breakpoints")
        _optional_get(base, "/api/v1/system/deployment/profiles")
        _optional_get(base, "/api/v1/system/deployment/safety")

    print("H-050 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

