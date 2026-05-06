"""
LEARNING: email_optimizer
PURPOSE: Analyze successful emails and generate improved templates via OpenAI (subject_template, email_template)
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


async def optimize_email_strategy(
    past_successful_emails: Optional[List[Dict[str, Any]]] = None,
    campaign_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Use OpenAI to generate optimized outreach templates from past successful emails and context.
    Returns subject_template, email_template.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        return {
            "subject_template": "Re: {{topic}} – quick question",
            "email_template": "Hi {{first_name}},\n\nI noticed {{company}} is active in {{industry}}. We help companies like yours with {{goal}}.\n\nWould you be open to a short conversation this week?\n\nBest,\n{{sender}}",
            "style": "short problem-solution",
        }

    context_str = json.dumps(campaign_context or {}, indent=0)[:500]
    examples = ""
    if past_successful_emails:
        for i, e in enumerate(past_successful_emails[:5]):
            subj = e.get("subject", e.get("outreach_subject", ""))
            body = e.get("body", e.get("outreach_body", e.get("email_body", "")))[:300]
            examples += f"\nExample {i+1} Subject: {subj}\nBody: {body}\n"

    prompt = (
        "You are a B2B sales expert. Based on the following campaign context and (if any) past successful outreach examples, "
        "output exactly two templates in JSON: subject_template (one line, use placeholders like {{first_name}}, {{company}}, {{industry}}, {{goal}}) "
        "and email_template (2-4 short sentences, same placeholders). Style: concise, problem-solution, professional.\n\n"
        f"Campaign context: {context_str}\n"
        f"{examples}\n"
        "Respond with only valid JSON: {\"subject_template\": \"...\", \"email_template\": \"...\"}"
    )
    try:
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400,
        )
        text = (resp.choices[0].message.content or "").strip()
        # Strip markdown code block if present
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        data = json.loads(text)
        return {
            "subject_template": data.get("subject_template", "Re: {{topic}}"),
            "email_template": data.get("email_template", ""),
            "style": "short problem-solution",
        }
    except Exception as e:
        logger.warning("optimize_email_strategy OpenAI failed: %s", e)
        return {
            "subject_template": "Re: {{topic}} – quick question",
            "email_template": "Hi {{first_name}},\n\nI noticed {{company}} is active in {{industry}}. We help with {{goal}}. Open to a short call?\n\nBest,\n{{sender}}",
            "style": "short problem-solution",
        }
