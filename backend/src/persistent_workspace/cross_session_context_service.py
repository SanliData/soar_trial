"""
MODULE: cross_session_context_service
PURPOSE: Cross-session continuity metadata — governed (H-042)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_cross_session_context_manifest() -> dict[str, Any]:
    return {
        "continuation_tokens": [
            {
                "token_id": "csc-001",
                "binds_state_types": ["workflow_state", "onboarding_state"],
                "ttl_hours": 168,
                "requires_explicit_resume": True,
            }
        ],
        "session_handoff_audit": True,
        "autonomous_long_running_sessions": False,
        "deterministic": True,
    }
