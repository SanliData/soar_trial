import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class FollowupStrategySkill(BaseSkill):
    name = "followup_strategy_skill"
    description = "Suggest follow-up strategy from classification; structured JSON in/out"
    inputs = ["classification", "confidence", "suggested_action"]
    outputs = ["followup_strategy", "next_step"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        classification = context.get("classification", "neutral")
        action = context.get("suggested_action", "")
        if classification == "positive":
            strategy = "send_calendar_link"
            next_step = "Book meeting within 48h"
        elif classification == "negative":
            strategy = "disqualify"
            next_step = "Remove from sequence"
        else:
            strategy = "send_followup_2"
            next_step = "Send follow-up in 5 days"
        logger.info("followup_strategy_skill: %s -> %s", classification, strategy)
        return {"followup_strategy": strategy, "next_step": next_step}
