"""
AGENTS: response_classification skill
PURPOSE: Classify reply email as positive_interest | neutral | not_now | not_interested + reasoning
"""
import json
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None

CLASSES = ["positive_interest", "neutral", "not_now", "not_interested"]


async def run_response_classification(reply_email_body: str) -> Dict[str, Any]:
    """
    Classify a reply email. Returns { "classification": str, "reasoning": str }.
    """
    logger.info("agent skill: response_classification start")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        logger.warning("response_classification: OPENAI not configured")
        return {"classification": "neutral", "reasoning": "OpenAI not configured."}

    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = (
            f"Classify this B2B reply email into exactly one of: {json.dumps(CLASSES)}. "
            "Then in one sentence explain why. "
            "Reply with only valid JSON: {\"classification\": \"...\", \"reasoning\": \"...\"}\n\n"
            f"Email:\n{reply_email_body[:2000]}"
        )
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200,
        )
        text = (resp.choices[0].message.content or "{}").strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {"classification": "neutral", "reasoning": "Parse failed."}
        if data.get("classification") not in CLASSES:
            data["classification"] = "neutral"
        logger.info("agent skill: response_classification done classification=%s", data.get("classification"))
        return data
    except Exception as e:
        logger.exception("response_classification failed: %s", e)
        return {"classification": "neutral", "reasoning": str(e)}
