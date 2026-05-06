"""
AGENTS: persona_detection skill
PURPOSE: Extract decision makers (CEO, CTO, Founder, Head of Infrastructure, Procurement Director) from company context
"""
import json
import logging
import os
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None

DEFAULT_ROLES = ["CEO", "CTO", "Founder", "Head of Infrastructure", "Procurement Director"]


async def run_persona_detection(
    companies: List[Dict[str, Any]],
    target_roles: List[str],
) -> Dict[str, Any]:
    """
    Use LLM to infer decision-maker personas per company. Returns companies with "personas" list.
    """
    logger.info("agent skill: persona_detection start companies=%s roles=%s", len(companies), target_roles)
    start = time.perf_counter()
    roles = target_roles or DEFAULT_ROLES
    api_key = os.getenv("OPENAI_API_KEY")
    token_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    if not api_key or not _OPENAI_AVAILABLE:
        logger.warning("persona_detection: OPENAI not configured, returning placeholder personas")
        out = []
        for c in companies:
            out.append({
                **c,
                "personas": [{"name": f"{r} (placeholder)", "role": r} for r in roles[:3]],
            })
        return {"companies": out, "token_usage": token_usage}

    try:
        client = openai.OpenAI(api_key=api_key)
        out = []
        for c in companies:
            name = c.get("name", "Unknown")
            insight = c.get("insight", {})
            context = insight.get("what_company_does", "") or name
            prompt = (
                f"Company: {name}. Context: {context}. "
                f"List 1-2 hypothetical decision makers for roles: {json.dumps(roles)}. "
                'Return only valid JSON array: [{"name":"...","role":"..."}, ...]'
            )
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=400,
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
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info("agent skill: persona_detection done latency_ms=%s", latency_ms)
        return {"companies": out, "token_usage": token_usage, "latency_ms": latency_ms}
    except Exception as e:
        logger.exception("persona_detection failed: %s", e)
        out = []
        for c in companies:
            out.append({
                **c,
                "personas": [{"name": f"{r} (fallback)", "role": r} for r in roles[:2]],
            })
        return {"companies": out, "token_usage": token_usage}
