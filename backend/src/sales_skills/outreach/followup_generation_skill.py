"""
SALES_SKILLS: followup_generation_skill
PURPOSE: Generate follow-up email or action based on reply classification
"""
import json
import logging
import os
from typing import Any, Dict

from src.sales_skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


class FollowupGenerationSkill(BaseSkill):
    name = "followup_generation"
    description = "Generate follow-up email or action based on classification"
    inputs = ["classification", "reasoning"]
    outputs = ["subject", "email_body", "suggested_action"]

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        classification = context.get("classification", "neutral")
        reasoning = context.get("reasoning", "")
        if not os.getenv("OPENAI_API_KEY") or not _OPENAI_AVAILABLE:
            return {
                "subject": "Re: Follow-up",
                "email_body": "Placeholder follow-up.",
                "suggested_action": "Send reminder in 2 weeks",
            }
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = (
                f"Reply classification: {classification}. Reasoning: {reasoning}. "
                "Suggest: (1) short follow-up subject, (2) 1-2 sentence body, (3) suggested_action. "
                "Return JSON: {\"subject\":\"...\",\"email_body\":\"...\",\"suggested_action\":\"...\"}"
            )
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=150,
            )
            text = (resp.choices[0].message.content or "{}").strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            data = json.loads(text)
            return {
                "subject": data.get("subject", "Re: Follow-up"),
                "email_body": data.get("email_body", ""),
                "suggested_action": data.get("suggested_action", ""),
            }
        except Exception as e:
            logger.exception("followup_generation: %s", e)
            return {
                "subject": "Re: Follow-up",
                "email_body": "Placeholder follow-up.",
                "suggested_action": "Send reminder in 2 weeks",
            }
