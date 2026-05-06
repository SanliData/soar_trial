"""
MODULE: channel_integration_policy
PURPOSE: Channel metadata policies (no live integrations) (H-050)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any


def export_channel_policies() -> dict[str, Any]:
    channels = [
        {"channel": "internal_web_ui", "external": False, "identity_required": True, "approval_required": False, "deterministic": True},
        {"channel": "slack", "external": True, "identity_required": True, "approval_required": True, "deterministic": True},
        {"channel": "telegram", "external": True, "identity_required": True, "approval_required": True, "deterministic": True},
        {"channel": "whatsapp", "external": True, "identity_required": True, "approval_required": True, "deterministic": True},
        {"channel": "discord", "external": True, "identity_required": True, "approval_required": True, "deterministic": True},
    ]
    return {"channels": channels, "deterministic": True, "metadata_only": True}

