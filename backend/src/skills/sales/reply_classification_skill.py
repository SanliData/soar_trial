import logging
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class ReplyClassificationSkill(BaseSkill):
    name = "reply_classification_skill"
    description = "Classify reply sentiment/interest; structured JSON in/out"
    inputs = ["reply_body", "reply_subject"]
    outputs = ["classification", "confidence", "suggested_action"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        body = context.get("reply_body", "")
        subj = context.get("reply_subject", "")
        classification = "neutral"
        confidence = 0.5
        if body and ("interested" in body.lower() or "yes" in body.lower() or "schedule" in body.lower()):
            classification = "positive"
            confidence = 0.8
        elif body and ("not interested" in body.lower() or "no thanks" in body.lower()):
            classification = "negative"
            confidence = 0.7
        action = "follow_up" if classification == "positive" else "nurture" if classification == "neutral" else "disqualify"
        logger.info("reply_classification_skill: %s (%.2f)", classification, confidence)
        return {"classification": classification, "confidence": confidence, "suggested_action": action}
