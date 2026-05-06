"""
MODULE: widget_render_service
PURPOSE: Deterministic HTML fragments — escaped text only, no scripts (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import html
import uuid
from datetime import datetime, timezone
from typing import Any

from src.intelligence_widgets.widget_contracts import IntelligenceWidget, WidgetRenderRequest
from src.intelligence_widgets.widget_state_service import record_widget_render
from src.intelligence_widgets.widget_validation_service import validate_render_request


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def _wrap_section(
    widget: IntelligenceWidget,
    inner: str,
) -> str:
    inter = "true" if widget.interactive else "false"
    return (
        f'<section class="iw-widget" data-widget-id="{_esc(widget.widget_id)}" '
        f'data-widget-type="{_esc(widget.widget_type)}" data-viz="{_esc(widget.visualization_type)}" '
        f'data-authority="{_esc(widget.authority_level)}" data-interactive="{inter}" '
        f'data-freshness-days="{widget.freshness_days}">{inner}</section>'
    )


def _tags_block(tags: list[str]) -> str:
    if not tags:
        return ""
    parts = ", ".join(_esc(t) for t in tags)
    return f'<p class="iw-tags"><span class="iw-muted">tags:</span> {_esc(parts)}</p>'


def render_widget(widget: IntelligenceWidget) -> str:
    """Emit a minimal deterministic HTML fragment."""
    title = _esc(widget.title)
    desc = _esc(widget.description) if widget.description else ""
    authority = _esc(widget.authority_level)
    viz = widget.visualization_type
    data = widget.data

    head = f'<header class="iw-head"><h3 class="iw-title">{title}</h3>'
    if desc:
        head += f'<p class="iw-desc">{desc}</p>'
    head += (
        f'<p class="iw-meta"><span class="iw-muted">authority:</span> {authority} '
        f'<span class="iw-muted">freshness_days:</span> {widget.freshness_days}</p>'
        f"</header>"
    )

    body_inner = ""
    if viz == "card":
        body_inner = _render_card_body(widget)
    elif viz == "chart":
        body_inner = _render_chart_body(widget)
    elif viz == "graph":
        body_inner = _render_graph_body(widget)
    elif viz == "timeline":
        body_inner = _render_timeline_body(widget)
    elif viz == "table":
        body_inner = _render_table_body(widget)
    elif viz == "map":
        body_inner = _render_map_body(widget)
    else:
        body_inner = '<p class="iw-placeholder">Unsupported visualization.</p>'

    inner = head + '<div class="iw-body">' + body_inner + "</div>" + _tags_block(widget.tags)
    return _wrap_section(widget, inner)


def _render_card_body(widget: IntelligenceWidget) -> str:
    rows = []
    for key in sorted(widget.data.keys()):
        val = widget.data[key]
        if isinstance(val, (str, int, float, bool)):
            rows.append(f"<li><strong>{_esc(str(key))}:</strong> {_esc(str(val))}</li>")
    if not rows:
        rows.append("<li class='iw-muted'>No structured fields.</li>")
    return f'<ul class="iw-card-fields">{"".join(rows)}</ul>'


def _render_chart_body(widget: IntelligenceWidget) -> str:
    series = widget.data.get("series")
    out = ['<div class="iw-chart" role="img" aria-label="deterministic chart placeholder">']
    if isinstance(series, list) and series:
        out.append("<table class='iw-chart-table'><thead><tr><th>label</th><th>value</th></tr></thead><tbody>")
        for row in series:
            if isinstance(row, dict):
                lab = _esc(str(row.get("label", "")))
                val = _esc(str(row.get("value", "")))
                out.append(f"<tr><td>{lab}</td><td>{val}</td></tr>")
        out.append("</tbody></table>")
    else:
        caption = _esc(str(widget.data.get("caption", "chart data")))
        out.append(f'<p class="iw-chart-caption">{caption}</p>')
    out.append("</div>")
    return "".join(out)


def _render_graph_body(widget: IntelligenceWidget) -> str:
    nodes = widget.data.get("nodes")
    edges = widget.data.get("edges")
    parts = ['<div class="iw-graph">']
    parts.append("<p class='iw-muted'>nodes</p><ul>")
    if isinstance(nodes, list):
        for n in nodes[:50]:
            parts.append(f"<li>{_esc(str(n))}</li>")
    else:
        parts.append("<li>(none)</li>")
    parts.append("</ul><p class='iw-muted'>edges</p><ul>")
    if isinstance(edges, list):
        for e in edges[:50]:
            if isinstance(e, dict):
                parts.append(
                    "<li>"
                    + _esc(str(e.get("from", "")))
                    + " → "
                    + _esc(str(e.get("to", "")))
                    + "</li>"
                )
            else:
                parts.append(f"<li>{_esc(str(e))}</li>")
    else:
        parts.append("<li>(none)</li>")
    parts.append("</ul></div>")
    return "".join(parts)


def _render_timeline_body(widget: IntelligenceWidget) -> str:
    events = widget.data.get("events")
    parts = ['<ol class="iw-timeline">']
    if isinstance(events, list):
        for ev in events:
            if isinstance(ev, dict):
                when = _esc(str(ev.get("date", ev.get("when", ""))))
                label = _esc(str(ev.get("label", ev.get("title", ""))))
                parts.append(f"<li><time>{when}</time> — <span>{label}</span></li>")
            else:
                parts.append(f"<li>{_esc(str(ev))}</li>")
    parts.append("</ol>")
    return "".join(parts)


def _render_table_body(widget: IntelligenceWidget) -> str:
    rows = widget.data.get("rows")
    if not isinstance(rows, list) or not rows:
        return '<p class="iw-muted">empty table</p>'
    first = rows[0]
    if not isinstance(first, dict):
        return '<p class="iw-muted">invalid rows</p>'
    keys = list(first.keys())
    parts = ['<table class="iw-table"><thead><tr>']
    for k in keys:
        parts.append(f"<th>{_esc(str(k))}</th>")
    parts.append("</tr></thead><tbody>")
    for row in rows:
        if not isinstance(row, dict):
            continue
        parts.append("<tr>")
        for k in keys:
            parts.append(f"<td>{_esc(str(row.get(k, '')))}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def _render_map_body(widget: IntelligenceWidget) -> str:
    region = widget.data.get("region") or widget.data.get("focus_region") or "unspecified"
    clusters = widget.data.get("clusters", [])
    c_html = ""
    if isinstance(clusters, list):
        c_html = "<ul>" + "".join(f"<li>{_esc(str(c))}</li>" for c in clusters[:20]) + "</ul>"
    return (
        f'<div class="iw-map" role="region" aria-label="map summary">'
        f"<p><strong>region:</strong> {_esc(str(region))}</p>{c_html}</div>"
    )


def render_widget_collection(widgets: list[IntelligenceWidget]) -> str:
    parts = ['<div class="iw-collection">']
    for w in widgets:
        parts.append(render_widget(w))
    parts.append("</div>")
    return "".join(parts)


def render_widget_summary(widgets: list[IntelligenceWidget]) -> dict[str, Any]:
    return {
        "count": len(widgets),
        "widget_types": sorted({w.widget_type for w in widgets}),
        "visualization_types": sorted({w.visualization_type for w in widgets}),
    }


def render_from_request(body: WidgetRenderRequest) -> tuple[IntelligenceWidget, str]:
    validate_render_request(body)
    wid = str(uuid.uuid4())
    widget = IntelligenceWidget(
        widget_id=wid,
        widget_type=body.widget_type,
        title=body.title,
        description=body.description,
        authority_level=body.authority_level,
        freshness_days=body.freshness_days,
        interactive=body.interactive,
        visualization_type=body.visualization_type,
        data=dict(body.data),
        created_at=datetime.now(timezone.utc),
        tags=list(body.tags),
    )
    fragment = render_widget(widget)
    record_widget_render(wid)
    return widget, fragment


def demo_widgets() -> list[IntelligenceWidget]:
    """Deterministic canned widgets for GET /demo — no randomness."""
    base_time = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    samples = [
        IntelligenceWidget(
            widget_id="demo-opportunity-cluster",
            widget_type="opportunity_cluster_map",
            title="EU manufacturing cluster",
            description="Three opportunity hotspots with bounded scores.",
            authority_level="high",
            freshness_days=12,
            interactive=False,
            visualization_type="map",
            data={"region": "EU", "clusters": ["Benelux advanced mfg", "DACH automation", "Nordic cleantech"]},
            created_at=base_time,
            tags=["opportunity", "geo"],
        ),
        IntelligenceWidget(
            widget_id="demo-market-signal",
            widget_type="market_signal_chart",
            title="Signal velocity",
            description="Category strengths (deterministic table representation).",
            authority_level="medium",
            freshness_days=30,
            interactive=False,
            visualization_type="chart",
            data={
                "series": [
                    {"label": "demand", "value": "0.72"},
                    {"label": "supply", "value": "0.54"},
                ]
            },
            created_at=base_time,
            tags=["signals"],
        ),
        IntelligenceWidget(
            widget_id="demo-graph",
            widget_type="graph_relationship_view",
            title="Supplier touchpoints",
            description="Curated edge list — no live graph engine.",
            authority_level="medium",
            freshness_days=7,
            interactive=False,
            visualization_type="graph",
            data={
                "nodes": ["Acme Corp", "Parts Ltd"],
                "edges": [{"from": "Acme Corp", "to": "Parts Ltd"}],
            },
            created_at=base_time,
            tags=["graph"],
        ),
        IntelligenceWidget(
            widget_id="demo-exec-card",
            widget_type="executive_summary_card",
            title="Executive briefing",
            description="Quarterly intelligence headline.",
            authority_level="high",
            freshness_days=3,
            interactive=False,
            visualization_type="card",
            data={"headline": "Pipeline stable", "risk": "low"},
            created_at=base_time,
            tags=["exec"],
        ),
        IntelligenceWidget(
            widget_id="demo-procurement",
            widget_type="procurement_timeline",
            title="Procurement milestones",
            description="Structured milestone ordering.",
            authority_level="high",
            freshness_days=45,
            interactive=False,
            visualization_type="timeline",
            data={
                "events": [
                    {"date": "2026-01-02", "label": "RFI published"},
                    {"date": "2026-02-01", "label": "Vendor shortlist"},
                ]
            },
            created_at=base_time,
            tags=["procurement"],
        ),
    ]
    return samples


def build_demo_payload() -> dict[str, Any]:
    widgets = demo_widgets()
    fragments = [render_widget(w) for w in widgets]
    return {
        "widgets": [w.model_dump(mode="json") for w in widgets],
        "html_fragments": fragments,
        "collection_html": render_widget_collection(widgets),
        "summary": render_widget_summary(widgets),
    }
