"""
MODULE: browser_automation_policy_service
PURPOSE: Sandboxed browser automation policies — no unrestricted browsing (H-037)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_browser_automation_policies() -> dict[str, Any]:
    return {
        "sandbox_required": True,
        "domain_allowlist": ["trusted-catalog.internal", "*.gov.example"],
        "rate_limit_rpm": 30,
        "execution_budget_tokens": 8000,
        "session_isolation": "strict_single_session",
        "replay_traces_required": True,
        "unrestricted_browser_automation": False,
        "deterministic_policy_version": "h037_browser_v1",
    }
