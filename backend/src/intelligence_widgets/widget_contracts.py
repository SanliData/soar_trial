"""
MODULE: widget_contracts
PURPOSE: Deterministic intelligence widget schemas (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_WIDGET_TYPES: frozenset[str] = frozenset(
    {
        "opportunity_cluster_map",
        "market_signal_chart",
        "executive_summary_card",
        "exposure_funnel",
        "graph_relationship_view",
        "procurement_timeline",
        "onboarding_progress",
    }
)

ALLOWED_VISUALIZATION_TYPES: frozenset[str] = frozenset(
    {
        "card",
        "chart",
        "graph",
        "timeline",
        "table",
        "map",
    }
)

AuthorityLevel = Literal["low", "medium", "high"]


class IntelligenceWidget(BaseModel):
    """Structured intelligence widget contract — no arbitrary HTML in fields."""

    widget_id: str
    widget_type: str
    title: str = Field(..., min_length=1)
    description: str = ""
    authority_level: AuthorityLevel
    freshness_days: int = Field(..., ge=0, le=3650)
    interactive: bool = False
    visualization_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    tags: list[str] = Field(default_factory=list)

    @field_validator("widget_type")
    @classmethod
    def widget_type_ok(cls, v: str) -> str:
        if v not in ALLOWED_WIDGET_TYPES:
            raise ValueError(f"invalid widget_type: {v}")
        return v

    @field_validator("visualization_type")
    @classmethod
    def viz_ok(cls, v: str) -> str:
        if v not in ALLOWED_VISUALIZATION_TYPES:
            raise ValueError(f"invalid visualization_type: {v}")
        return v


class WidgetRenderRequest(BaseModel):
    """Inbound render request — server assigns widget_id and created_at."""

    widget_type: str
    title: str = Field(..., min_length=1)
    description: str = ""
    authority_level: AuthorityLevel
    freshness_days: int = Field(..., ge=0, le=3650)
    interactive: bool = False
    visualization_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
