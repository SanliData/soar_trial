"""
NL_QUERY: question_parser
PURPOSE: Parse natural language into structured intent (no user text in SQL)
Output: tables, group_by, metric, time_range — used only to drive planner/sql_generator.
"""
import logging
import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ParsedIntent(BaseModel):
    """Structured intent from NL question; only these fields drive SQL generation."""
    tables: List[str] = Field(default_factory=list, description="Requested tables (e.g. intel_companies, campaigns)")
    group_by: Optional[str] = Field(None, description="Column or concept to group by (e.g. industry, campaign)")
    metric: Optional[str] = Field(None, description="Metric: reply_rate, count, most_replies, etc.")
    time_range: Optional[str] = Field(None, description="last_quarter, last_month, last_week, or null")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Strict key-value filters from whitelist only")
    limit: int = Field(default=50, ge=1, le=500)


***REMOVED*** Allowed table names for analytics (whitelist)
ALLOWED_TABLES = frozenset({
    "intel_companies", "intel_contacts", "intel_campaigns",
    "companies", "campaigns", "leads", "industry_performance",
    "email_performance", "campaign_history", "users",
})

***REMOVED*** Map keywords to table names
TABLE_HINTS = {
    "industry": ["intel_companies", "industry_performance"],
    "industries": ["intel_companies", "industry_performance"],
    "company": ["intel_companies", "companies"],
    "companies": ["intel_companies", "companies"],
    "contact": ["intel_contacts"],
    "contacts": ["intel_contacts"],
    "campaign": ["campaigns", "intel_campaigns", "campaign_history", "email_performance"],
    "campaigns": ["campaigns", "intel_campaigns", "campaign_history", "email_performance"],
    "reply": ["email_performance", "campaign_history"],
    "replies": ["email_performance", "campaign_history"],
    "outreach": ["campaigns", "email_performance"],
    "cto": ["intel_contacts"],
    "texas": ["intel_companies", "companies"],
    "rate": ["email_performance", "industry_performance"],
}

***REMOVED*** Map keywords to group_by concept (column chosen in planner from allowed columns)
GROUP_HINTS = {
    "industry": "industry",
    "industries": "industry",
    "campaign": "campaign",
    "campaigns": "campaign",
    "company": "company",
}

***REMOVED*** Time expressions
TIME_HINTS = {
    "last quarter": "last_quarter",
    "last month": "last_month",
    "last week": "last_week",
    "past quarter": "last_quarter",
    "past month": "last_month",
}


def _normalize(s: str) -> str:
    return " ".join(s.lower().split()) if s else ""


def parse_question(question: str) -> ParsedIntent:
    """
    Parse NL question into ParsedIntent. No user-supplied text is used in SQL;
    only whitelisted tables/columns and structured filters (e.g. time) are used.
    """
    if not question or not isinstance(question, str):
        return ParsedIntent(tables=[], limit=50)
    text = _normalize(question)
    tables_set = set()
    for keyword, tbls in TABLE_HINTS.items():
        if keyword in text:
            for t in tbls:
                if t in ALLOWED_TABLES:
                    tables_set.add(t)
    tables = list(tables_set) if tables_set else ["intel_companies", "campaigns", "email_performance"]

    group_by = None
    for kw, g in GROUP_HINTS.items():
        if kw in text:
            group_by = g
            break

    metric = None
    if "reply rate" in text or "reply rate" in text or "reply_rate" in text:
        metric = "reply_rate"
    elif "most reply" in text or "highest reply" in text or "most replies" in text:
        metric = "most_replies"
    elif "count" in text or "how many" in text or "number of" in text:
        metric = "count"
    elif "best" in text or "respond best" in text:
        metric = "reply_rate"

    time_range = None
    for phrase, tr in TIME_HINTS.items():
        if phrase in text:
            time_range = tr
            break

    return ParsedIntent(
        tables=sorted(tables),
        group_by=group_by,
        metric=metric or "count",
        time_range=time_range,
        limit=50,
    )
