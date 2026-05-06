"""
AUTOMATION: followup_engine
PURPOSE: Generate follow-up (subject, body, suggested_action) by classification; uses agent followup_generation
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def schedule_followup(
    classification: str,
    reasoning: str,
    contact_id: Optional[str] = None,
    original_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Plan follow-up: subject, body, suggested_action. Uses agents.skills.followup_generation.
    """
    try:
        from src.agents.skills.followup_generation import run_followup_generation
        result = await run_followup_generation(classification, reasoning)
        return {
            "subject": result.get("subject"),
            "body": result.get("body"),
            "suggested_action": result.get("suggested_action"),
        }
    except Exception as e:
        logger.warning("schedule_followup failed: %s", e)
        return {"subject": None, "body": None, "suggested_action": None}
