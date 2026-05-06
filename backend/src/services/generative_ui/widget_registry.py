"""Allowlist of widget types for controlled generative UI (H-019)."""

from typing import FrozenSet


ALLOWED_WIDGET_TYPES: FrozenSet[str] = frozenset(
    {
        "executive_briefing",
        "graph_summary",
        "market_signal_cockpit",
        "opportunity_cluster",
    }
)


def is_allowed_widget(widget_type: str) -> bool:
    return widget_type in ALLOWED_WIDGET_TYPES
