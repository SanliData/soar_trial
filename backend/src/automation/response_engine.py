"""
AUTOMATION: response_engine (response_classifier)
PURPOSE: Classify reply emails (positive_interest | neutral | not_now | not_interested) via agent skill
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def process_incoming_response(
    email_body: str,
    thread_id: Optional[str] = None,
    contact_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Classify incoming reply and optionally suggest follow-up. Uses agents.skills.response_classification.
    """
    try:
        from src.agents.skills.response_classification import run_response_classification
        result = await run_response_classification(email_body)
        classification = result.get("classification", "neutral")
        reasoning = result.get("reasoning", "")
        followup_suggested = None
        try:
            from src.agents.skills.followup_generation import run_followup_generation
            followup_suggested = await run_followup_generation(classification, reasoning)
        except Exception as e:
            logger.debug("followup_generation in response_engine: %s", e)
        return {
            "classification": classification,
            "reasoning": reasoning,
            "followup_suggested": followup_suggested,
        }
    except Exception as e:
        logger.warning("process_incoming_response failed: %s", e)
        return {"classification": "neutral", "reasoning": str(e), "followup_suggested": None}
