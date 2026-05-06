"""
AGENTS: persona_extraction skill
PURPOSE: Extract decision makers (CEO, CTO, etc.) using OpenAI; returns structured JSON
"""
import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


async def run_persona_extraction(
    companies: List[Dict[str, Any]],
    decision_roles: List[str],
) -> Dict[str, Any]:
    """
    Use OpenAI to infer decision-maker personas per company.
    Returns JSON: { "companies": [ { "name": "...", "website": "...", "personas": [ { "name", "role" } ] } ] }
    """
    logger.info("agent skill: persona_extraction start companies=%s roles=%s", len(companies), decision_roles)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        logger.warning("persona_extraction: OPENAI_API_KEY not configured, returning placeholder personas")
        # Graceful fallback: generic personas per company
        out = []
        for c in companies:
            out.append({
                "name": c.get("name", "Unknown"),
                "website": c.get("website"),
                "personas": [{"name": f"{r} (placeholder)", "role": r} for r in decision_roles[:2]],
            })
        return {"companies": out}

    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = (
            "For each company, list 1-2 hypothetical decision makers with the given roles. "
            "Return only valid JSON with no markdown.\n"
            "Companies: " + json.dumps(companies) + "\n"
            "Roles: " + json.dumps(decision_roles) + "\n"
            "Format: {\"companies\": [{\"name\": \"...\", \"website\": \"...\", \"personas\": [{\"name\": \"...\", \"role\": \"...\"}]}]}"
        )
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=800,
        )
        text = resp.choices[0].message.content or "{}"
        usage = getattr(resp, "usage", None)
        if usage:
            logger.info("agent skill: persona_extraction openai usage prompt_tokens=%s completion_tokens=%s",
                       getattr(usage, "prompt_tokens", 0), getattr(usage, "completion_tokens", 0))
        # Strip possible markdown code block
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        data = json.loads(text)
        logger.info("agent skill: persona_extraction done")
        return data
    except Exception as e:
        logger.exception("persona_extraction failed: %s", e)
        # Graceful fallback
        out = []
        for c in companies:
            out.append({
                "name": c.get("name", "Unknown"),
                "website": c.get("website"),
                "personas": [{"name": f"{r} (fallback)", "role": r} for r in decision_roles[:2]],
            })
        return {"companies": out}
