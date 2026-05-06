"""
AGENTS: company_analysis skill
PURPOSE: Use LLM to analyze company context (what they do, pain points, outreach relevance)
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


async def run_company_analysis(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze each company with LLM: what they do, pain points, why outreach is relevant.
    Returns { "companies": [ { ...company, "insight": { "what_company_does", "pain_points", "outreach_relevance" } } ] }
    """
    logger.info("agent skill: company_analysis start companies=%s", len(companies))
    start = time.perf_counter()
    api_key = os.getenv("OPENAI_API_KEY")
    token_usage = {"prompt_tokens": 0, "completion_tokens": 0}

    if not api_key or not _OPENAI_AVAILABLE:
        logger.warning("company_analysis: OPENAI not configured, returning placeholder insights")
        out = []
        for c in companies:
            out.append({
                **c,
                "insight": {
                    "what_company_does": "Placeholder (configure OPENAI_API_KEY for analysis).",
                    "pain_points": "Infrastructure scaling, cost efficiency.",
                    "outreach_relevance": "Relevant for B2B services.",
                },
            })
        return {"companies": out, "token_usage": token_usage}

    try:
        client = openai.OpenAI(api_key=api_key)
        out = []
        for c in companies:
            name = c.get("name", "Unknown")
            industry = c.get("industry", "")
            location = c.get("location", "")
            prompt = (
                f"For the company '{name}' (industry: {industry}, location: {location}), "
                "provide in 1-2 sentences each: (1) what the company does, (2) potential pain points, "
                "(3) why B2B outreach would be relevant. Return only valid JSON: "
                '{"what_company_does":"...","pain_points":"...","outreach_relevance":"..."}'
            )
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300,
            )
            text = (resp.choices[0].message.content or "{}").strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            try:
                insight = json.loads(text)
            except json.JSONDecodeError:
                insight = {"what_company_does": text[:200], "pain_points": "", "outreach_relevance": ""}
            if resp.usage:
                token_usage["prompt_tokens"] += getattr(resp.usage, "prompt_tokens", 0)
                token_usage["completion_tokens"] += getattr(resp.usage, "completion_tokens", 0)
            out.append({**c, "insight": insight})
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info("agent skill: company_analysis done latency_ms=%s", latency_ms)
        return {"companies": out, "token_usage": token_usage, "latency_ms": latency_ms}
    except Exception as e:
        logger.exception("company_analysis failed: %s", e)
        out = []
        for c in companies:
            out.append({
                **c,
                "insight": {
                    "what_company_does": "",
                    "pain_points": "",
                    "outreach_relevance": "Analysis failed.",
                },
            })
        return {"companies": out, "token_usage": token_usage}
