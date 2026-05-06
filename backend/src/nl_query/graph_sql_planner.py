"""
NL_QUERY: graph_sql_planner
PURPOSE: Use intelligence graph to choose tables and join path for the query plan
"""
import logging
from typing import List, Optional

from pydantic import BaseModel

from src.intelligence_graph.graph_query_engine import get_join_path, get_table_columns, list_tables
from src.nl_query.question_parser import ALLOWED_TABLES, ParsedIntent

logger = logging.getLogger(__name__)


class QueryPlan(BaseModel):
    """Plan: ordered tables, join path [from_t, to_t, from_col, to_col], select columns [table, col], group_by, metric."""
    tables: List[str] = []
    joins: List[List[str]] = []
    select_columns: List[List[str]] = []
    group_by_table: Optional[str] = None
    group_by_column: Optional[str] = None
    metric: str = "count"
    time_range: Optional[str] = None
    limit: int = 50

    class Config:
        arbitrary_types_allowed = True


def _resolve_group_column(intent: ParsedIntent, tables: List[str]) -> tuple:
    """Resolve group_by to (table_name, column_name) from allowed columns."""
    want = (intent.group_by or "").strip().lower()
    if not want:
        return None, None
    valid = list_tables()
    for t in tables:
        if t not in valid:
            continue
        cols = get_table_columns(t)
        for c in cols:
            if want in c.lower() or (want == "industry" and c in ("industry", "industry_name", "sector")):
                return t, c
            if want == "campaign" and c in ("campaign_id", "name", "campaign_name"):
                return t, c
    return None, None


def plan_sql(intent: ParsedIntent) -> QueryPlan:
    """
    Build query plan from intent using the schema graph.
    Picks a connected set of tables and a valid join path; never uses user text in SQL.
    """
    requested = [t for t in intent.tables if t in ALLOWED_TABLES]
    if not requested:
        requested = ["intel_companies", "email_performance"]
    tables_used = list(dict.fromkeys(requested))
    joins = []
    seen_edges = set()
    if len(tables_used) >= 2:
        base = tables_used[0]
        for i in range(1, len(tables_used)):
            target = tables_used[i]
            path = get_join_path(base, target)
            if path:
                for ft, tt, fc, tc in path:
                    key = (ft, tt, fc, tc)
                    if key not in seen_edges:
                        seen_edges.add(key)
                        joins.append([ft, tt, fc, tc])
    select_columns = []
    for t in tables_used:
        cols = get_table_columns(t)
        for c in cols:
            if c in ("id", "created_at", "updated_at", "name", "industry", "reply_count", "sent_count", "open_count"):
                select_columns.append([t, c])
        if not any(sc[0] == t for sc in select_columns) and cols:
            select_columns.append([t, cols[0]])
    gt, gc = _resolve_group_column(intent, tables_used)
    return QueryPlan(
        tables=tables_used,
        joins=joins,
        select_columns=select_columns[:20],
        group_by_table=gt,
        group_by_column=gc,
        metric=intent.metric or "count",
        time_range=intent.time_range,
        limit=intent.limit,
    )
