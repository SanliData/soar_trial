"""
AGENTS: followup_generation skill
PURPOSE: Generate next follow-up email based on classification (meeting scheduling, clarification, reminder)
"""
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


async def run_followup_generation(
    classification: str,
    reasoning: str,
    original_context: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate follow-up email based on classification:
    - positive_interest -> meeting scheduling
    - neutral -> clarification
    - not_now -> reminder in 3 weeks
    Returns { "subject": str, "body": str, "suggested_action": str }
    """
    logger.info("agent skill: followup_generation start classification=%s", classification)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        return {
            "subject": "Follow-up",
            "body": "Thank you for your reply. We would be happy to discuss further at your convenience.",
            "suggested_action": "Send when ready.",
        }

    try:
        client = openai.OpenAI(api_key=api_key)
        if classification == "positive_interest":
            intent = "Suggest scheduling a short meeting or call. Be concise and offer 2-3 time options."
        elif classification == "neutral":
            intent = "Ask one short clarifying question to understand their needs better."
        elif classification == "not_now":
            intent = "Write a brief, friendly reminder that you will follow up in 3 weeks. No pressure."
        else:
            intent = "Write a one-line polite sign-off, leaving door open for future."
        prompt = (
            f"Their reply was classified as: {classification}. Reasoning: {reasoning}. "
            f"Generate a follow-up email. Intent: {intent}. "
            "First line: Subject: ... then blank line then body. Short and professional."
        )
        if original_context:
            prompt += f"\nOriginal context: {original_context[:200]}"
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=250,
        )
        text = (resp.choices[0].message.content or "").strip()
        subject, body = "Follow-up", text
        if "Subject:" in text:
            parts = text.split("Subject:", 1)
            if len(parts) > 1:
                subject = parts[1].strip().split("\n")[0].strip()
                body = "\n".join(parts[1].strip().split("\n")[1:]).strip()
        suggested = "Schedule meeting" if classification == "positive_interest" else "Send when appropriate"
        logger.info("agent skill: followup_generation done")
        return {"subject": subject, "body": body, "suggested_action": suggested}
    except Exception as e:
        logger.exception("followup_generation failed: %s", e)
        return {"subject": "Follow-up", "body": "We will follow up at a better time.", "suggested_action": "Retry later."}