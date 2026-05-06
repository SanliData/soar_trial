"""
ROUTER: generative_ui_router
PURPOSE: Controlled generative UI render endpoint (H-019 foundation)
ENCODING: UTF-8 WITHOUT BOM

Router layer: dependency injection, validation (Pydantic), error mapping only.
Business logic lives in src.services.generative_ui.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from src.http.v1.b2b_api_router import validate_api_key
from src.services.generative_ui.schemas import GenerativeUiRenderRequest, GenerativeUiRenderResponse
from src.services.generative_ui.generation_service import generate_render_response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["generative-ui"])


@router.post(
    "/generative-ui/render",
    response_model=GenerativeUiRenderResponse,
    summary="Render a template-bound generative widget (sandbox-ready HTML)",
)
async def render_generative_ui_widget(
    body: GenerativeUiRenderRequest,
    _api_key: str = Depends(validate_api_key),
) -> GenerativeUiRenderResponse:
    try:
        return generate_render_response(body)
    except ValueError as e:
        logger.info("generative_ui validation failed: %s", e)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        logger.exception("generative_ui render failed")
        raise HTTPException(status_code=500, detail="Render failed") from e
