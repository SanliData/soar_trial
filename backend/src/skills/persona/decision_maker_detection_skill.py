"""
SKILLS: decision_maker_detection_skill
PURPOSE: Extract likely decision makers (CEO, CTO, Founder, Procurement Director, VP Operations) -> structured persona objects
"""
import json
import logging
import os
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

EXPECTED_ROLES = ["CEO", "CTO", "Founder", "Procurement Director", "VP Operations"]

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


class DecisionMakerDetectionSkill(BaseSkill):
    name = "decision_maker_detection"
    description = "Extract decision-maker personas per company"
    inputs = ["companies"]
    outputs = ["companies", "token_usage"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        roles = context.get("target_roles") or EXPECTED_ROLES
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        if not os.getenv("OPENAI_API_KEY") or not _OPENAI_AVAILABLE:
            out = []
            for c in companies:
                out.append({
                    **c,
                    "personas": [{"name": f"{r} (placeholder)", "role": r} for r in roles[:3]],
                })
            return {"companies": out, "token_usage": token_usage}
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            out = []
            for c in companies:
                name = c.get("name", "Unknown")
                summary = c.get("company_summary", "") or c.get("name", "")
                prompt = (
                    f"Company: {name}. Context: {summary}. "
                    f"List 1-2 hypothetical decision makers for roles: {json.dumps(roles)}. "
                    'Return only valid JSON array: [{"name":"...","role":"..."}, ...]'
                )
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300,
                )
                text = (resp.choices[0].message.content or "[]").strip()
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()
                try:
                    personas = json.loads(text)
                except json.JSONDecodeError:
                    personas = [{"name": f"{r} (fallback)", "role": r} for r in roles[:2]]
                if resp.usage:
                    token_usage["prompt_tokens"] += getattr(resp.usage, "prompt_tokens", 0)
                    token_usage["completion_tokens"] += getattr(resp.usage, "completion_tokens", 0)
                out.append({**c, "personas": personas})
            return {"companies": out, "token_usage": token_usage}
        except Exception as e:
            logger.warning("decision_maker_detection_skill: %s", e)
            out = []
            for c in companies:
                out.append({**c, "personas": [{"name": f"{r} (fallback)", "role": r} for r in roles[:3]]})
            return {"companies": out, "token_usage": token_usage}
