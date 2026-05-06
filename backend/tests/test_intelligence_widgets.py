"""
TEST: intelligence_widgets (H-025)
PURPOSE: Deterministic widget registry and safe rendering
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.app import create_app

os.environ.setdefault("JWT_SECRET", "test-h025-jwt-secret-32characters-required!")
os.environ["SOARB2B_API_KEYS"] = "test-h025-widgets-key"

from src.intelligence_widgets.widget_contracts import IntelligenceWidget
from src.intelligence_widgets.widget_registry import export_registry_public, list_registered_widget_types
from src.intelligence_widgets.widget_render_service import (
    demo_widgets,
    render_widget,
    render_widget_collection,
    render_widget_summary,
)
from src.intelligence_widgets.widget_state_service import clear_state_for_tests

clear_state_for_tests()
app = create_app()
client = TestClient(app)

BASE = "/api/v1/system/widgets"


@pytest.fixture(autouse=True)
def _reset_state():
    clear_state_for_tests()
    yield


def test_valid_widget_accepted():
    body = {
        "widget_type": "executive_summary_card",
        "title": "Quarter outlook",
        "description": "Structured briefing.",
        "authority_level": "high",
        "freshness_days": 5,
        "interactive": False,
        "visualization_type": "card",
        "data": {"kpi": "stable"},
        "tags": ["exec"],
    }
    r = client.post(f"{BASE}/render", json=body)
    assert r.status_code == 200
    data = r.json()
    assert data["deterministic_rendering"] is True
    assert data["script_injection_blocked"] is True
    assert "html_fragment" in data
    assert "<script" not in data["html_fragment"].lower()


def test_invalid_widget_type_rejected():
    body = {
        "widget_type": "unknown_widget",
        "title": "x",
        "authority_level": "low",
        "freshness_days": 1,
        "visualization_type": "card",
    }
    r = client.post(f"{BASE}/render", json=body)
    assert r.status_code == 422


def test_invalid_visualization_rejected():
    body = {
        "widget_type": "executive_summary_card",
        "title": "x",
        "authority_level": "low",
        "freshness_days": 1,
        "visualization_type": "map",
    }
    r = client.post(f"{BASE}/render", json=body)
    assert r.status_code == 422


def test_rendering_escapes_unsafe_html_in_title():
    body = {
        "widget_type": "executive_summary_card",
        "title": '<img src=x onerror="alert(1)">Brief',
        "description": "d",
        "authority_level": "medium",
        "freshness_days": 2,
        "interactive": False,
        "visualization_type": "card",
        "data": {},
    }
    r = client.post(f"{BASE}/render", json=body)
    assert r.status_code == 200
    frag = r.json()["html_fragment"]
    assert "<img" not in frag
    assert "&lt;img" in frag


def test_deterministic_rendering_consistent():
    w = demo_widgets()[0]
    a = render_widget(w)
    b = render_widget(w)
    assert a == b


def test_widget_registry_works():
    types = list_registered_widget_types()
    assert "executive_summary_card" in types
    blob = export_registry_public()
    assert "widget_types" in blob
    assert len(blob["widget_types"]) == 7


def test_widget_summary_works():
    ws = demo_widgets()[:2]
    s = render_widget_summary(ws)
    assert s["count"] == 2
    assert len(s["widget_types"]) >= 1


def test_collection_wraps_sections():
    html = render_widget_collection(demo_widgets()[:2])
    assert 'class="iw-collection"' in html
    assert html.count("iw-widget") == 2


def test_types_and_demo_endpoints():
    r1 = client.get(f"{BASE}/types")
    r2 = client.get(f"{BASE}/demo")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["deterministic_rendering"] is True
    assert "html_fragments" in r2.json()


def test_script_like_payload_rejected():
    body = {
        "widget_type": "executive_summary_card",
        "title": "clean",
        "authority_level": "low",
        "freshness_days": 1,
        "visualization_type": "card",
        "data": {"bad": "<script>x</script>"},
    }
    r = client.post(f"{BASE}/render", json=body)
    assert r.status_code == 422


def test_authority_levels_validated_via_contract():
    with pytest.raises(ValidationError):
        IntelligenceWidget(
            widget_id="x",
            widget_type="executive_summary_card",
            title="t",
            authority_level="invalid",  ***REMOVED*** type: ignore[arg-type]
            freshness_days=1,
            visualization_type="card",
            created_at=demo_widgets()[0].created_at,
        )
