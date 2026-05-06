"""
AGENTS: email_generation skill
PURPOSE: Generate personalized outreach email per contact using OpenAI; returns structured JSON
"""
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


async def run_email_generation(
    companies: List[Dict[str, Any]],
    context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate one short outreach email per contact using OpenAI.
    context can contain industry, location for personalization.
    Returns same structure with generated_email added per contact.
    """
    logger.info("agent skill: email_generation start companies=%s", len(companies))
    industry = context.get("industry", "")
    location = context.get("location", "")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE:
        logger.warning("email_generation: OPENAI not configured, skipping generated emails")
        for c in companies:
            for contact in c.get("contacts", []):
                contact["generated_email"] = None
        return {"companies": companies}

    try:
        client = openai.OpenAI(api_key=api_key)
        out = []
        for c in companies:
            contacts = []
            for contact in c.get("contacts", []):
                name = contact.get("name", "there")
                role = contact.get("role", "Decision Maker")
                company = c.get("name", "your company")
                prompt = (
                    f"Write one short (2-3 sentences) B2B outreach email. "
                    f"Recipient: {name}, {role} at {company}. Industry: {industry}. Location: {location}. "
                    "Tone: professional, concise. No subject line, only body."
                )
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=150,
                )
                body = (resp.choices[0].message.content or "").strip()
                usage = getattr(resp, "usage", None)
                if usage:
                    logger.debug("email_generation token usage: %s", usage)
                contacts.append({
                    **contact,
                    "generated_email": body or None,
                })
            out.append({**c, "contacts": contacts})
        logger.info("agent skill: email_generation done")
        return {"companies": out}
    except Exception as e:
        logger.exception("email_generation failed: %s", e)
        for c in companies:
            for contact in c.get("contacts", []):
                contact["generated_email"] = None
        return {"companies": companies}


async def run_outreach_email_generation(
    companies: List[Dict[str, Any]],
    campaign_goal: str,
    email_strategy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate subject + email_body per contact for sales engine. Human, concise, relevant.
    If email_strategy (from learning engine) has subject_template/email_template, use them as style guidance.
    Returns { "companies": [...], "token_usage": {...}, "latency_ms": N }
    """
    logger.info("agent skill: outreach_email_generation start companies=%s goal=%s", len(companies), campaign_goal[:50])
    start = time.perf_counter()
    api_key = os.getenv("OPENAI_API_KEY")
    token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    if not api_key or not _OPENAI_AVAILABLE:
        for c in companies:
            for contact in c.get("contacts", []):
                contact["outreach_subject"] = None
                contact["outreach_body"] = None
        return {"companies": companies, "token_usage": token_usage}

    strategy_guidance = ""
    if email_strategy:
        subj = email_strategy.get("subject_template") or ""
        body = email_strategy.get("email_template") or ""
        style = email_strategy.get("style") or "short problem-solution"
        if subj or body:
            strategy_guidance = f" Preferred style: {style}. Use placeholders like {{first_name}}, {{company}}, {{industry}}, {{goal}}. Example subject style: {subj[:80]}. Example body style: {body[:150]}."

    try:
        client = openai.OpenAI(api_key=api_key)
        out = []
        for c in companies:
            insight = c.get("insight", {})
            company_context = (insight.get("what_company_does") or c.get("name", ""))[:300]
            contacts = []
            for contact in c.get("contacts", []):
                name = contact.get("name", "there")
                role = contact.get("role", "Decision Maker")
                company = c.get("name", "your company")
                prompt = (
                    f"Campaign goal: {campaign_goal}. "
                    f"Recipient: {name}, {role} at {company}. Company context: {company_context}. "
                    "Write one B2B outreach email: first line must be the subject (Subject: ...), then a blank line, then 2-3 sentence body. Human, concise, relevant."
                    f"{strategy_guidance}"
                )
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=250,
                )
                text = (resp.choices[0].message.content or "").strip()
                if resp.usage:
                    token_usage["prompt_tokens"] += getattr(resp.usage, "prompt_tokens", 0)
                    token_usage["completion_tokens"] += getattr(resp.usage, "completion_tokens", 0)
                subject, body = "", text
                if "Subject:" in text:
                    parts = text.split("Subject:", 1)
                    if len(parts) > 1:
                        first_line = parts[1].strip().split("\n")[0].strip()
                        subject = first_line
                        body = "\n".join(parts[1].strip().split("\n")[1:]).strip()
                contacts.append({
                    **contact,
                    "outreach_subject": subject or "Re: Introduction",
                    "outreach_body": body or text,
                })
            out.append({**c, "contacts": contacts})
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info("agent skill: outreach_email_generation done latency_ms=%s", latency_ms)
        return {"companies": out, "token_usage": token_usage, "latency_ms": latency_ms}
    except Exception as e:
        logger.exception("outreach_email_generation failed: %s", e)
        for c in companies:
            for contact in c.get("contacts", []):
                contact["outreach_subject"] = None
                contact["outreach_body"] = None
        return {"companies": companies, "token_usage": token_usage}
