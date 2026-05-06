"""Deterministic, template-bound HTML generation. Escapes all dynamic text."""

from __future__ import annotations

import html as html_lib

from src.services.generative_ui.schemas import GenerativeUiRenderRequest, GenerativeUiRenderResponse
from src.services.generative_ui.validation_service import validate_render_request


_ROOT_CLASS = "genui-widget"


def _e(s: str) -> str:
    return html_lib.escape((s or ""), quote=True)


def _render_metrics(metrics) -> str:
    if not metrics:
        return ""
    rows = "".join(
        f'<div class="{_ROOT_CLASS}-metric"><span class="{_ROOT_CLASS}-ml">{_e(m.label)}</span>'
        f'<span class="{_ROOT_CLASS}-mv">{_e(m.value)}</span></div>'
        for m in metrics
    )
    return f'<div class="{_ROOT_CLASS}-metrics">{rows}</div>'


def _render_recommendations(items: list[str]) -> str:
    if not items:
        return ""
    lis = "".join(f'<li class="{_ROOT_CLASS}-li">{_e(x)}</li>' for x in items)
    return f'<ul class="{_ROOT_CLASS}-ul">{lis}</ul>'


def render_executive_briefing(body: GenerativeUiRenderRequest) -> str:
    summary_trim = (body.summary or "").strip()
    sum_html = (
        f'<p class="{_ROOT_CLASS}-summary">{_e(summary_trim)}</p>' if summary_trim else ""
    )
    return (
        f'<section class="{_ROOT_CLASS} {_ROOT_CLASS}-executive" data-widget="executive_briefing">'
        f'<h3 class="{_ROOT_CLASS}-title">{_e(body.title)}</h3>'
        f'{sum_html}'
        f'{_render_metrics(body.metrics)}'
        f'<div class="{_ROOT_CLASS}-reco-h">Recommendations</div>'
        f'{_render_recommendations(body.recommendations)}'
        f'</section>'
    )


def render_graph_summary(body: GenerativeUiRenderRequest) -> str:
    nodes_block = ""
    if body.graph_nodes:
        spans = "".join(
            f'<span class="{_ROOT_CLASS}-node" data-ref="{_e(n.node_id)}">{_e(n.label)}</span>'
            for n in body.graph_nodes
        )
        nodes_block = f'<div class="{_ROOT_CLASS}-nodes">{spans}</div>'
    edges_block = ""
    if body.graph_edges:
        parts = []
        for edge in body.graph_edges:
            parts.append(f'{_e(edge.source_id)} &rarr; {_e(edge.target_id)}')
        edges_block = f'<div class="{_ROOT_CLASS}-edges">' + "; ".join(parts) + "</div>"
    summary = _e((body.summary or "").strip())
    sum_html = f'<p class="{_ROOT_CLASS}-summary">{summary}</p>' if summary else ""
    return (
        f'<section class="{_ROOT_CLASS} {_ROOT_CLASS}-graph" data-widget="graph_summary">'
        f'<h3 class="{_ROOT_CLASS}-title">{_e(body.title)}</h3>'
        f'{sum_html}'
        f'{nodes_block}'
        f'{edges_block}'
        f'{_render_metrics(body.metrics)}'
        f'</section>'
    )


def render_market_signal_cockpit(body: GenerativeUiRenderRequest) -> str:
    signals_html = ""
    if body.signals:
        rows = ""
        for s in body.signals:
            rows += (
                f'<div class="{_ROOT_CLASS}-signal" data-severity="{_e(s.severity)}">'
                f'<strong>{_e(s.name)}</strong> '
                f'<span class="{_ROOT_CLASS}-sd">{_e(s.detail)}</span></div>'
            )
        signals_html = f'<div class="{_ROOT_CLASS}-signals">{rows}</div>'
    summary = _e((body.summary or "").strip())
    sum_html = f'<p class="{_ROOT_CLASS}-summary">{summary}</p>' if summary else ""
    return (
        f'<section class="{_ROOT_CLASS} {_ROOT_CLASS}-cockpit" data-widget="market_signal_cockpit">'
        f'<h3 class="{_ROOT_CLASS}-title">{_e(body.title)}</h3>'
        f'{sum_html}'
        f'{signals_html}'
        f'{_render_metrics(body.metrics)}'
        f'</section>'
    )


def render_opportunity_cluster(body: GenerativeUiRenderRequest) -> str:
    clusters_html = ""
    if body.clusters:
        blocks = ""
        for c in body.clusters:
            note = _e(c.note.strip())
            note_block = f'<div class="{_ROOT_CLASS}-cn">{note}</div>' if note else ""
            blocks += (
                f'<div class="{_ROOT_CLASS}-cluster">'
                f'<strong>{_e(c.label)}</strong> '
                f'<span class="{_ROOT_CLASS}-cc">{_e(c.count)}</span>'
                f'{note_block}</div>'
            )
        clusters_html = f'<div class="{_ROOT_CLASS}-clusters">{blocks}</div>'
    summary = _e((body.summary or "").strip())
    sum_html = f'<p class="{_ROOT_CLASS}-summary">{summary}</p>' if summary else ""
    return (
        f'<section class="{_ROOT_CLASS} {_ROOT_CLASS}-opp" data-widget="opportunity_cluster">'
        f'<h3 class="{_ROOT_CLASS}-title">{_e(body.title)}</h3>'
        f'{sum_html}'
        f'{clusters_html}'
        f'{_render_metrics(body.metrics)}'
        f'{_render_recommendations(body.recommendations)}'
        f'</section>'
    )


RENDERERS = {
    "executive_briefing": render_executive_briefing,
    "graph_summary": render_graph_summary,
    "market_signal_cockpit": render_market_signal_cockpit,
    "opportunity_cluster": render_opportunity_cluster,
}


def generate_widget_html(body: GenerativeUiRenderRequest) -> str:
    validated = validate_render_request(body)
    renderer = RENDERERS.get(validated.widget_type)
    if not renderer:
        raise ValueError("unknown widget_type")
    return renderer(validated)


def generate_render_response(body: GenerativeUiRenderRequest) -> GenerativeUiRenderResponse:
    """Public entry: validated structured input -> sanitized HTML snippet + flags."""
    html = generate_widget_html(body)
    ***REMOVED*** Hard guarantees for consumers (embedding in sandboxed iframe)
    return GenerativeUiRenderResponse(
        widget_type=body.widget_type,
        html=html,
        sandbox_required=True,
        runtime_js_allowed=False,
    )
