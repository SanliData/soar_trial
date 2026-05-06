"""
TEST: generative_ui (H-019)
PURPOSE: Controlled generative UI foundation — template-bound HTML only
ENCODING: UTF-8 WITHOUT BOM

Import `create_app` before assigning SOARB2B_API_KEYS: `src.app` runs
load_dotenv(override=True) on import, which overwrites earlier env assignments.
"""
import os

import pytest
from fastapi.testclient import TestClient

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-12345-for-generative-ui-tests")
os.environ["SOARB2B_API_KEYS"] = "test-genui-api-key"

app = create_app()
client = TestClient(app)

HEADERS = {"X-API-Key": "test-genui-api-key", "Content-Type": "application/json"}

_RENDER_PATH = "/api/v1/b2b/generative-ui/render"


@pytest.fixture
def executive_payload():
    return {
        "widget_type": "executive_briefing",
        "title": "Dallas Industrial Bakery Opportunity",
        "summary": "High concentration of relevant manufacturers...",
        "metrics": [
            {"label": "Eligible companies", "value": "84"},
            {"label": "Contact coverage", "value": "62%"},
        ],
        "recommendations": [
            "Prioritize North Dallas clusters",
            "Use owner/operator persona first",
        ],
    }


def test_executive_briefing_renders(executive_payload):
    r = client.post(_RENDER_PATH, json=executive_payload, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["widget_type"] == "executive_briefing"
    assert data["sandbox_required"] is True
    assert data["runtime_js_allowed"] is False
    assert "genui-widget" in data["html"]
    assert "Dallas Industrial Bakery" in data["html"]
    assert "<script" not in data["html"].lower()


def test_graph_summary_renders():
    payload = {
        "widget_type": "graph_summary",
        "title": "Graph snapshot",
        "summary": "Key relationships in this plan.",
        "graph_nodes": [{"id": "c1", "label": "Acme Co"}, {"id": "c2", "label": "Beta LLC"}],
        "graph_edges": [{"source_id": "c1", "target_id": "c2"}],
    }
    r = client.post(_RENDER_PATH, json=payload, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["widget_type"] == "graph_summary"
    assert data["sandbox_required"] is True
    assert data["runtime_js_allowed"] is False
    assert "Acme Co" in data["html"]


def test_unknown_widget_type_validation_error():
    r = client.post(
        _RENDER_PATH,
        json={"widget_type": "malicious_widget", "title": "x"},
        headers=HEADERS,
    )
    assert r.status_code == 422


def test_graph_summary_validation_missing_nodes_and_summary():
    r = client.post(
        _RENDER_PATH,
        json={"widget_type": "graph_summary", "title": "Bad", "summary": "   "},
        headers=HEADERS,
    )
    assert r.status_code == 422
    assert "graph_nodes" in str(r.json()).lower() or "graph_summary" in str(r.json()).lower()


def test_xss_escaped_in_output(executive_payload):
    executive_payload["title"] = '<script>alert(1)</script>'
    executive_payload["summary"] = '<img src=x onerror=alert(1)>'
    r = client.post(_RENDER_PATH, json=executive_payload, headers=HEADERS)
    assert r.status_code == 200
    html = r.json()["html"]
    assert "<script" not in html.lower()
    assert "&lt;script" in html or "script&gt;" in html or "&lt;img" in html


def test_requires_api_key(executive_payload):
    r = client.post(_RENDER_PATH, json=executive_payload)
    assert r.status_code == 401


def test_market_signal_cockpit_renders():
    payload = {
        "widget_type": "market_signal_cockpit",
        "title": "Signals",
        "summary": "Regional hiring intensity increased week over week.",
        "signals": [{"name": "Hiring spike", "severity": "info", "detail": "+logistics roles"}],
        "metrics": [],
    }
    r = client.post(_RENDER_PATH, json=payload, headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["runtime_js_allowed"] is False


def test_opportunity_cluster_renders():
    payload = {
        "widget_type": "opportunity_cluster",
        "title": "Clusters",
        "summary": "",
        "clusters": [{"label": "North", "count": "12", "note": "Higher reply rates"}],
    }
    r = client.post(_RENDER_PATH, json=payload, headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert data["sandbox_required"] is True
    assert "North" in data["html"]
