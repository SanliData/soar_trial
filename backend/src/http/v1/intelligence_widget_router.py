"""
ROUTER: intelligence_widget_router
PURPOSE: HTTP facade for intelligence widgets (H-025)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.intelligence_widgets.widget_contracts import WidgetRenderRequest
from src.intelligence_widgets.widget_registry import export_registry_public
from src.intelligence_widgets.widget_render_service import build_demo_payload, render_from_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/widgets", tags=["intelligence-widgets"])


def _envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"deterministic_rendering": True, "script_injection_blocked": True}
    out.update(payload)
    return out


@router.post("/render")
async def post_render_widget(body: WidgetRenderRequest) -> Dict[str, Any]:
    try:
        widget, html_fragment = render_from_request(body)
        return _envelope(
            {
                "widget": widget.model_dump(mode="json"),
                "html_fragment": html_fragment,
            }
        )
    except ValueError as exc:
        logger.info("widget render rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/types")
async def get_widget_types() -> Dict[str, Any]:
    return _envelope(export_registry_public())


@router.get("/demo")
async def get_widget_demo() -> Dict[str, Any]:
    return _envelope(build_demo_payload())
