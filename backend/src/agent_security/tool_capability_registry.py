"""
MODULE: tool_capability_registry
PURPOSE: Static tool capability catalog — no runtime mutation (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

TRUST_LEVELS: frozenset[str] = frozenset(
    {
        "verified_internal",
        "trusted_partner",
        "external_unverified",
        "sandbox_only",
    }
)


class ToolCapability(BaseModel):
    tool_name: str
    trust_level: str
    allowed_actions: list[str] = Field(default_factory=list)
    external_execution: bool = False
    requires_human_approval: bool = False
    allowed_domains: list[str] = Field(default_factory=list)
    risk_level: str = "low"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def _fixed_ts() -> datetime:
    """Deterministic timestamp for registry snapshots (RFC audit consistency)."""
    return datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


***REMOVED*** Immutable definitions — created_at frozen for deterministic exports
TOOL_REGISTRY: dict[str, ToolCapability] = {
    "results_hub_read": ToolCapability(
        tool_name="results_hub_read",
        trust_level="verified_internal",
        allowed_actions=["read_plan", "list_companies"],
        external_execution=False,
        requires_human_approval=False,
        allowed_domains=["internal.api"],
        risk_level="low",
        created_at=_fixed_ts(),
    ),
    "graph_traverse": ToolCapability(
        tool_name="graph_traverse",
        trust_level="verified_internal",
        allowed_actions=["neighbour_query", "path_hint"],
        external_execution=False,
        requires_human_approval=False,
        allowed_domains=["internal.graph"],
        risk_level="low",
        created_at=_fixed_ts(),
    ),
    "market_feed_pull": ToolCapability(
        tool_name="market_feed_pull",
        trust_level="trusted_partner",
        allowed_actions=["fetch_digest"],
        external_execution=True,
        requires_human_approval=False,
        allowed_domains=["partner.vendor.example"],
        risk_level="medium",
        created_at=_fixed_ts(),
    ),
    "web_fetch_unverified": ToolCapability(
        tool_name="web_fetch_unverified",
        trust_level="external_unverified",
        allowed_actions=["fetch_url"],
        external_execution=True,
        requires_human_approval=True,
        allowed_domains=[],  ***REMOVED*** explicit host allow-list enforced elsewhere
        risk_level="high",
        created_at=_fixed_ts(),
    ),
    "experimental_tool": ToolCapability(
        tool_name="experimental_tool",
        trust_level="sandbox_only",
        allowed_actions=["dry_run"],
        external_execution=False,
        requires_human_approval=True,
        allowed_domains=["sandbox.local"],
        risk_level="high",
        created_at=_fixed_ts(),
    ),
}


def export_capabilities_manifest() -> dict[str, Any]:
    tools = sorted(TOOL_REGISTRY.values(), key=lambda t: t.tool_name)
    return {
        "tools": [t.model_dump(mode="json") for t in tools],
        "trust_levels": sorted(TRUST_LEVELS),
    }


def get_tool_capability(tool_name: str) -> ToolCapability | None:
    return TOOL_REGISTRY.get(tool_name)
