"""
ROUTER: ai_runtime_router
PURPOSE: Deterministic AI runtime profile API (H-021 foundation)
ENCODING: UTF-8 WITHOUT BOM

Router delegates to ai_runtime services only — no branching policy stored here.
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from src.ai_runtime.inference_profile_service import build_inference_profile
from src.ai_runtime.runtime_schema import (
    AIRuntimeProfilesListResponse,
    AIRuntimeProfileResponse,
    ProfileBuildRequest,
)
from src.ai_runtime.runtime_telemetry_service import list_recent_profiles, record_profile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system/ai-runtime", tags=["ai-runtime"])


@router.post("/profile", response_model=AIRuntimeProfileResponse)
async def create_ai_runtime_profile(body: ProfileBuildRequest) -> AIRuntimeProfileResponse:
    try:
        profile = build_inference_profile(body.task, body.input_context)
        record_profile(profile)
        return AIRuntimeProfileResponse(llm_invoked=False, profile=profile)
    except ValueError as exc:
        logger.info("ai_runtime profile validation failed: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/profiles", response_model=AIRuntimeProfilesListResponse)
async def recent_ai_runtime_profiles(
    limit: int = Query(20, ge=1, le=200),
) -> AIRuntimeProfilesListResponse:
    rows = list_recent_profiles(limit)
    return AIRuntimeProfilesListResponse(llm_invoked=False, profiles=rows)
