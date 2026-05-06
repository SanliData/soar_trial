"""
SALES_SKILLS: email_generation_skill
PURPOSE: Generate personalized outreach email per contact (company, role, campaign_goal -> subject, email_body)
"""
import logging
import os
from typing import Any, Dict, List

from src.sales_skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


class EmailGenerationSkill(BaseSkill):
    name = "email_generation"
    description = "Generate personalized outreach email per contact"
    inputs = ["companies", "campaign_goal"]
    outputs = ["companies", "token_usage"]

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        campaign_goal = context.get("campaign_goal", "")
        api_key = os.getenv("OPENAI_API_KEY")
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        if not api_key or not _OPENAI_AVAILABLE:
            for c in companies:
                for contact in c.get("contacts", c.get("selected_contacts", [])):
                    contact["subject"] = "Re: Introduction"
                    contact["email_body"] = "Placeholder (configure OPENAI_API_KEY)."
            return {"companies": companies, "token_usage": token_usage}
        try:
            client = openai.OpenAI(api_key=api_key)
            out = []
            for c in companies:
                profile = c.get("company_summary", "") or c.get("name", "")
                contacts = c.get("contacts", c.get("selected_contacts", []))
                generated = []
                for contact in contacts:
                    name = contact.get("name", "there")
                    role = contact.get("role", "Decision Maker")
                    prompt = (
                        f"Campaign goal: {campaign_goal}. Company: {profile}. "
                        f"Recipient: {name}, {role}. "
                        "Write one short B2B email: first line Subject: ..., then 2-3 sentence body. Natural and concise."
                    )
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5,
                        max_tokens=200,
                    )
                    text = (resp.choices[0].message.content or "").strip()
                    if resp.usage:
                        token_usage["prompt_tokens"] += getattr(resp.usage, "prompt_tokens", 0)
                        token_usage["completion_tokens"] += getattr(resp.usage, "completion_tokens", 0)
                    subject, body = "Re: Introduction", text
                    if "Subject:" in text:
                        parts = text.split("Subject:", 1)
                        if len(parts) > 1:
                            subject = parts[1].strip().split("\n")[0].strip()
                            body = "\n".join(parts[1].strip().split("\n")[1:]).strip()
                    generated.append({**contact, "subject": subject, "email_body": body or text})
                out.append({**c, "contacts": generated})
            return {"companies": out, "token_usage": token_usage}
        except Exception as e:
            logger.exception("email_generation: %s", e)
            return {"companies": companies, "token_usage": token_usage, "_errors": [str(e)]}
