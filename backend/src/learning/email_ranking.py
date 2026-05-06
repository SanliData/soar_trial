"""
LEARNING: email_ranking
PURPOSE: Use OpenAI as judge model to rank outreach email variants; store results for learning
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


async def rank_email_variants(
    variants: List[Dict[str, Any]],
    question: str = "Which email is most likely to get a reply?",
) -> Dict[str, Any]:
    """
    Given 2+ email variants (each with subject, body), ask OpenAI judge to rank them.
    Returns ranking (best first) and reasoning. Store result via learning engine for future campaigns.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or not _OPENAI_AVAILABLE or len(variants) < 2:
        return {"ranking": [0], "scores": [0.5], "reasoning": "OpenAI not configured or < 2 variants"}
    texts = []
    for i, v in enumerate(variants):
        subj = v.get("subject", "")
        body = (v.get("body") or v.get("email_body", ""))[:500]
        texts.append(f"Variant {i+1}:\nSubject: {subj}\nBody: {body}")
    prompt = (
        "You are a B2B sales expert. Below are outreach email variants.\n\n"
        + "\n\n---\n\n".join(texts)
        + f"\n\n{question} Return only valid JSON: "
        '{"ranking": [1,2,3], "reasoning": "one sentence", "scores": [0.9, 0.6, 0.4]} '
        "(ranking = variant indices 1-based in order of best to worst; scores 0-1 per variant)"
    )
    try:
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
        )
        text = (resp.choices[0].message.content or "{}").strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        data = json.loads(text)
        return {
            "ranking": data.get("ranking", list(range(1, len(variants) + 1))),
            "scores": data.get("scores", []),
            "reasoning": data.get("reasoning", ""),
        }
    except Exception as e:
        logger.warning("email_ranking failed: %s", e)
        return {"ranking": list(range(1, len(variants) + 1)), "scores": [], "reasoning": str(e)}


def store_ranking_result(campaign_id: str, variant_index: int, score: float, reasoning: str) -> None:
    """Persist ranking result for learning (email_performance or dedicated table)."""
    try:
        from src.db.base import SessionLocal
        from src.models.email_performance import EmailPerformance
        db = SessionLocal()
        try:
            db.add(EmailPerformance(
                campaign_id=campaign_id,
                email_variant_index=variant_index,
                judge_score=score,
                judge_reasoning=reasoning,
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.debug("store_ranking_result: %s", e)
