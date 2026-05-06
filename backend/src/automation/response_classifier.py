"""
AUTOMATION: response_classifier
PURPOSE: Classify reply emails (positive_interest | neutral | not_now | not_interested)
"""
import logging
from typing import Any, Dict

from src.automation.response_engine import process_incoming_response

logger = logging.getLogger(__name__)


async def classify_response(email_body: str, thread_id: str = None, contact_id: str = None) -> Dict[str, Any]:
    """
    Classify an incoming reply. Uses response_engine (which uses agents.skills.response_classification).
    """
    result = await process_incoming_response(
        email_body=email_body,
        thread_id=thread_id,
        contact_id=contact_id,
    )
    return {
        "classification": result.get("classification", "neutral"),
        "reasoning": result.get("reasoning", ""),
        "followup_suggested": result.get("followup_suggested"),
    }
