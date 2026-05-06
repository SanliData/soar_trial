"""Validate structured payloads per widget type. No raw HTML."""

from src.services.generative_ui.schemas import GenerativeUiRenderRequest
from src.services.generative_ui.widget_registry import is_allowed_widget


def validate_render_request(body: GenerativeUiRenderRequest) -> GenerativeUiRenderRequest:
    """
    Normalize and enforce per-widget structural rules.
    Raises ValueError with a safe detail string on failure.
    """
    wt = body.widget_type
    if not is_allowed_widget(wt):
        raise ValueError("unknown widget_type")

    if wt == "graph_summary":
        if not body.graph_nodes and not (body.summary or "").strip():
            raise ValueError("graph_summary requires graph_nodes or summary")
        if body.graph_edges and not body.graph_nodes:
            raise ValueError("graph_edges requires graph_nodes")

    if wt == "market_signal_cockpit":
        if not body.signals and not (body.summary or "").strip():
            raise ValueError("market_signal_cockpit requires signals or summary")

    if wt == "opportunity_cluster":
        if not body.clusters and not (body.summary or "").strip():
            raise ValueError("opportunity_cluster requires clusters or summary")

    return body
