"""
SERVICE: hs_code_service
PURPOSE: Ensure every plan/query has HS code (gümrük kodu) for archive; AI fills if user does not.
ENCODING: UTF-8 WITHOUT BOM
"""

import logging
from typing import Dict, Any

from src.services.gemini_analysis_service import get_gemini_analysis_service

logger = logging.getLogger(__name__)

# Keys in onboarding_data for HS / product customs
HS_CODE_KEY = "hs_code"
HS_CODE_SOURCE_KEY = "hs_code_source"
PRODUCT_CUSTOMS_DESCRIPTION_KEY = "product_customs_description"


def ensure_hs_code_in_onboarding(onboarding_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure onboarding_data has hs_code (and related fields). Required for every query/archive.
    If user already provided hs_code, keep it and set hs_code_source = "user".
    Otherwise call AI to infer and set hs_code, hs_code_source = "ai", product_customs_description.
    Modifies and returns the same dict (no copy).
    """
    if not onboarding_data:
        onboarding_data = {}
    if onboarding_data.get(HS_CODE_KEY) and (onboarding_data.get(HS_CODE_KEY) or "").strip():
        onboarding_data[HS_CODE_SOURCE_KEY] = onboarding_data.get(HS_CODE_SOURCE_KEY) or "user"
        if not onboarding_data.get(PRODUCT_CUSTOMS_DESCRIPTION_KEY):
            onboarding_data[PRODUCT_CUSTOMS_DESCRIPTION_KEY] = f"User-provided HS {onboarding_data[HS_CODE_KEY]}"
        return onboarding_data
    # AI inference
    gemini = get_gemini_analysis_service()
    product_service = onboarding_data.get("product_service") or onboarding_data.get("product_type") or ""
    target_type = onboarding_data.get("target_type") or ""
    geography = onboarding_data.get("geography") or onboarding_data.get("target_region") or ""
    industry = onboarding_data.get("industry")
    result = gemini.infer_hs_code(
        product_service=product_service,
        target_type=target_type,
        geography=geography,
        industry=industry,
    )
    onboarding_data[HS_CODE_KEY] = result.get("hs_code") or "9999"
    onboarding_data[HS_CODE_SOURCE_KEY] = "ai"
    onboarding_data[PRODUCT_CUSTOMS_DESCRIPTION_KEY] = result.get("description") or "Other / Unclassified"
    logger.info("HS code set for plan (AI): %s", onboarding_data.get(HS_CODE_KEY))
    return onboarding_data
