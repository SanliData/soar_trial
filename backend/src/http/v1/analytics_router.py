import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.analytics.domain import AnalyticsEvent
from src.db.base import get_db
from src.nl_query.question_parser import parse_question
from src.nl_query.graph_sql_planner import plan_sql
from src.nl_query.sql_generator import generate_sql
from src.nl_query.query_validator import validate_sql
from src.nl_query.query_safety import (
    validate_query_complexity,
    limit_join_depth,
    enforce_plan_limits,
    apply_result_limit,
    get_query_timeout_seconds,
)
from src.nl_query.response_formatter import format_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AnalyticsQueryRequest(BaseModel):
    """Request body for natural language analytics query."""
    question: str = Field(..., min_length=1, max_length=2000, description="Natural language question")


class AnalyticsQueryResponse(BaseModel):
    """Response: sql_used, result rows, and optional summary."""
    sql_used: str
    result: List[Dict[str, Any]]
    summary: str


def _run_query_sync(session: Session, sql: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Execute parameterized SQL and return list of dicts. Runs in sync context."""
    r = session.execute(text(sql), params or {})
    rows = r.fetchall()
    out = []
    for row in rows:
        if hasattr(row, "_mapping"):
            out.append(dict(row._mapping))
        elif hasattr(row, "_asdict"):
            out.append(row._asdict())
        else:
            out.append({"value": row})
    return out


@router.get("/health")
def health():
    return {
        "status": "ok",
        "domain": "analytics"
    }


@router.post("/query", response_model=AnalyticsQueryResponse)
async def analytics_query(
    body: AnalyticsQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Answer a natural language question over SOARB2B sales data.
    Returns sql_used, result rows, and a short summary. SQL is validated and parameterized.
    """
    question = (body.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    try:
        intent = parse_question(question)
    except Exception as e:
        logger.warning("nl_query_parsing_error: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail="Could not parse question.") from e
    try:
        plan = plan_sql(intent)
    except Exception as e:
        logger.warning("graph_sql_planner error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Query planning failed.") from e
    ok, err = validate_query_complexity(plan)
    if not ok:
        logger.warning("query_safety: %s", err)
        raise HTTPException(status_code=400, detail=f"Query complexity: {err}")
    plan = limit_join_depth(plan)
    plan = enforce_plan_limits(plan)
    try:
        sql, params = generate_sql(plan)
    except Exception as e:
        logger.warning("invalid_sql_generation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="SQL generation failed.") from e
    ok, err = validate_sql(sql)
    if not ok:
        logger.warning("invalid_sql_generation: %s", err)
        raise HTTPException(status_code=400, detail=f"Query validation failed: {err}")
    query_timeout = get_query_timeout_seconds()
    try:
        loop = asyncio.get_event_loop()
        rows = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _run_query_sync(db, sql, params)),
            timeout=query_timeout,
        )
        rows = apply_result_limit(rows)
    except asyncio.TimeoutError:
        logger.warning("query_timeout: analytics query exceeded %ss", query_timeout)
        raise HTTPException(status_code=504, detail="Query timed out.") from None
    except Exception as e:
        logger.exception("analytics_query_failure: %s", e)
        raise HTTPException(status_code=500, detail="Query execution failed.") from e
    formatted = format_response(rows, summary="")
    return AnalyticsQueryResponse(
        sql_used=sql,
        result=formatted["result"],
        summary=formatted["summary"],
    )


@router.post("/events")
def ingest_event(payload: Dict[str, Any]):
    try:
        event = AnalyticsEvent(
            event_type=payload.get("event_type"),
            occurred_at=datetime.utcnow(),
            entity_id=payload.get("entity_id"),
            payload=payload.get("payload", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "entity_id": event.entity_id,
    }
