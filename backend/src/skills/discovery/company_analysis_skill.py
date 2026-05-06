"""
SKILLS: company_analysis_skill
PURPOSE: OpenAI analysis -> company_summary, potential_pain_points, relevance_score
"""
import json
import logging
import os
from typing import Any, Dict, List

from src.skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)

_OPENAI_AVAILABLE = False
try:
    import openai
    _OPENAI_AVAILABLE = True
except ImportError:
    openai = None


class CompanyAnalysisSkill(BaseSkill):
    name = "company_analysis"
    description = "Analyze company context with LLM: summary, pain points, relevance"
    inputs = ["companies"]
    outputs = ["companies", "token_usage"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        companies = context.get("companies", [])
        api_key = os.getenv("OPENAI_API_KEY")
        token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        if not api_key or not _OPENAI_AVAILABLE:
            out = []
            for c in companies:
                out.append({
                    **c,
                    "company_summary": "Placeholder (configure OPENAI_API_KEY).",
                    "potential_pain_points": "Infrastructure scaling, cost efficiency.",
                    "relevance_score": 0.7,
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
                    f"Company: {name}, industry: {industry}, location: {location}. "
                    "Return only valid JSON: {\"company_summary\":\"1-2 sentences\",\"potential_pain_points\":\"1-2 sentences\",\"relevance_score\":0.0-1.0}"
                )
                resp = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=200,
                )
                text = (resp.choices[0].message.content or "{}").strip()
                if "```" in text:
                    text = text.split("```")[1].replace("json", "").strip()
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    data = {"company_summary": text[:150], "potential_pain_points": "", "relevance_score": 0.6}
                if resp.usage:
                    token_usage["prompt_tokens"] += getattr(resp.usage, "prompt_tokens", 0)
                    token_usage["completion_tokens"] += getattr(resp.usage, "completion_tokens", 0)
                out.append({
                    **c,
                    "company_summary": data.get("company_summary", ""),
                    "potential_pain_points": data.get("potential_pain_points", ""),
                    "relevance_score": float(data.get("relevance_score", 0.6)),
                })
            return {"companies": out, "token_usage": token_usage}
        except Exception as e:
            logger.warning("company_analysis_skill: %s", e)
            out = []
            for c in companies:
                out.append({
                    **c,
                    "company_summary": str(c.get("name", "")),
                    "potential_pain_points": "",
                    "relevance_score": 0.5,
                })
            return {"companies": out, "token_usage": token_usage}
