"""Pydantic schemas for structured generative UI payloads (no raw HTML accepted). UTF-8, English-only."""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


WIDGET_TYPES = Literal[
    "executive_briefing",
    "graph_summary",
    "market_signal_cockpit",
    "opportunity_cluster",
]


class MetricItem(BaseModel):
    label: str = Field(..., max_length=128)
    value: str = Field(..., max_length=256)


class SignalItem(BaseModel):
    name: str = Field(..., max_length=160)
    severity: str = Field(default="info", max_length=32)
    detail: str = Field(default="", max_length=640)


class ClusterItem(BaseModel):
    label: str = Field(..., max_length=160)
    count: str = Field(..., max_length=64)
    note: str = Field(default="", max_length=320)


class GraphNodeRef(BaseModel):
    node_id: str = Field(..., max_length=128, alias="id")
    label: str = Field(..., max_length=256)

    model_config = {"populate_by_name": True}


class GraphEdgeRef(BaseModel):
    """Directed edge expressed as structured endpoints (no raw HTML)."""

    source_id: str = Field(..., max_length=128)
    target_id: str = Field(..., max_length=128)


class GenerativeUiRenderRequest(BaseModel):
    widget_type: WIDGET_TYPES
    title: str = Field(..., max_length=200)
    summary: str = Field(default="", max_length=8000)
    metrics: List[MetricItem] = Field(default_factory=list, max_length=24)
    recommendations: List[str] = Field(default_factory=list, max_length=60)
    graph_nodes: Optional[List[GraphNodeRef]] = None
    graph_edges: Optional[List[GraphEdgeRef]] = None
    signals: Optional[List[SignalItem]] = None
    clusters: Optional[List[ClusterItem]] = None

    @field_validator("recommendations", mode="before")
    @classmethod
    def truncate_reco_strings(cls, v):
        if v is None:
            return []
        if not isinstance(v, list):
            return v
        out = []
        for item in v:
            if isinstance(item, str):
                out.append(item[:2000])
        return out


class GenerativeUiRenderResponse(BaseModel):
    widget_type: str
    html: str
    sandbox_required: bool = True
    runtime_js_allowed: bool = False
