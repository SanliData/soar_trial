import logging
import os
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class OutreachGenerationSkill(BaseSkill):
    name = "outreach_generation_skill"
    description = "Generate outreach content per contact; structured JSON in/out"
    inputs = ["companies", "enriched_contacts", "campaign_goal"]
    outputs = ["companies", "outreach_content", "token_usage"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        contacts = context.get("enriched_contacts", context.get("selected_contacts", []))
        goal = context.get("campaign_goal", "")
        outreach = []
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        if os.getenv("OPENAI_API_KEY"):
            try:
                import openai
                client = openai.AsyncOpenAI()
                for co in contacts[:20]:
                    prompt = "Campaign: %s. Contact: %s, %s. Write one short B2B subject and 2-sentence body." % (goal, co.get("name"), co.get("role"))
                    r = await client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=150)
                    text = (r.choices[0].message.content or "").strip()
                    outreach.append({"contact_id": co.get("contact_id"), "subject": "Re: Introduction", "body": text})
                    if r.usage:
                        token_usage["prompt_tokens"] += getattr(r.usage, "prompt_tokens", 0)
                        token_usage["completion_tokens"] += getattr(r.usage, "completion_tokens", 0)
            except Exception as e:
                logger.exception("outreach_generation_skill: %s", e)
        if not outreach:
            outreach = [{"contact_id": c.get("contact_id"), "subject": "Re: Introduction", "body": "Placeholder."} for c in contacts[:20]]
        return {"companies": companies, "outreach_content": outreach, "token_usage": token_usage}
