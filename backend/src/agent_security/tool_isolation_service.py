"""
MODULE: tool_isolation_service
PURPOSE: Explicit delegation allow-list — no implicit tool chains (H-029)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

# Directed pairs (source_tool -> target_tool) permitted for orchestration graphs.
ALLOWED_DELEGATIONS: frozenset[tuple[str, str]] = frozenset(
    {
        ("results_hub_read", "graph_traverse"),
        ("graph_traverse", "results_hub_read"),
        ("market_feed_pull", "results_hub_read"),
    }
)


def assert_delegation_allowed(source_tool: str, target_tool: str) -> dict[str, str | bool]:
    pair = (source_tool, target_tool)
    if pair not in ALLOWED_DELEGATIONS:
        raise ValueError(f"delegation blocked: {source_tool} → {target_tool} not explicitly allowed")
    return {"source_tool": source_tool, "target_tool": target_tool, "delegation_ok": True}


def hidden_activation_blocked(tool_name: str, implicit_chain: list[str]) -> None:
    """Reject implicit multi-hop activation without recorded delegation edges."""
    if len(implicit_chain) > 1:
        for i in range(len(implicit_chain) - 1):
            assert_delegation_allowed(implicit_chain[i], implicit_chain[i + 1])
