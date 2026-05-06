"""
ROUTER: generative_operational_ui_router
PURPOSE: Governed generative operational UI facade (H-048)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

from src.generative_operational_ui.chart_generation_service import export_charts
from src.generative_operational_ui.dashboard_generation_service import export_dashboards
from src.generative_operational_ui.graph_visualization_service import export_graph_views
from src.generative_operational_ui.ui_component_registry import export_ui_component_registry

router = APIRouter(prefix="/system/generative-ui", tags=["generative-ui"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "generative_operational_ui_foundation": True,
        "registry_only_components": True,
        "no_raw_html_generation": True,
        "no_raw_js_execution": True,
        "deterministic": True,
    }
    out.update(payload)
    return out


@router.get("/components")
async def get_components() -> Dict[str, Any]:
    return _envelope(export_ui_component_registry())


@router.get("/dashboards")
async def get_dashboards() -> Dict[str, Any]:
    return _envelope(export_dashboards())


@router.get("/charts")
async def get_charts() -> Dict[str, Any]:
    return _envelope(export_charts())


@router.get("/graphs")
async def get_graphs() -> Dict[str, Any]:
    return _envelope(export_graph_views())

