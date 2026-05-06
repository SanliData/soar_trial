"""
NL_QUERY: sql_generator
PURPOSE: Build parameterized SQL from QueryPlan only (no user text in SQL)
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.nl_query.graph_sql_planner import QueryPlan

logger = logging.getLogger(__name__)


def _time_bounds(time_range: Optional[str]) -> tuple:
    """Return (start_date, end_date) for time_range; values are safe for parameter binding."""
    now = datetime.utcnow()
    if time_range == "last_quarter":
        end = now
        start = now - timedelta(days=92)
    elif time_range == "last_month":
        end = now
        start = now - timedelta(days=31)
    elif time_range == "last_week":
        end = now
        start = now - timedelta(days=7)
    else:
        return None, None
    return start.date().isoformat(), end.date().isoformat()


def generate_sql(plan: QueryPlan) -> tuple:
    """
    Generate parameterized SQL and params from plan.
    Returns (sql: str, params: dict). SQL uses only whitelisted identifiers from plan.
    """
    if not plan.tables:
        return "SELECT 1", {}
    aliases = {}
    for i, t in enumerate(plan.tables):
        aliases[t] = f"t{i}"
    parts = []
    for item in plan.select_columns:
        if len(item) != 2:
            continue
        t, c = item[0], item[1]
        if t in aliases:
            parts.append(f'"{t}".{c} AS "{t}_{c}"')
    if not parts:
        parts = [f'"{plan.tables[0]}".id AS id']
    select_clause = ", ".join(parts)
    from_clause = f'"{plan.tables[0]}"'
    params = {}
    for j in plan.joins:
        if len(j) != 4:
            continue
        ft, tt, fc, tc = j[0], j[1], j[2], j[3]
        from_clause += f' JOIN "{tt}" ON "{ft}".{fc} = "{tt}".{tc}'
    where_parts = []
    start_d, end_d = _time_bounds(plan.time_range)
    if start_d and end_d:
        for t in plan.tables:
            if t in aliases:
                where_parts.append(f'("{t}".created_at IS NULL OR "{t}".created_at >= :start_date AND "{t}".created_at <= :end_date)')
                break
        params["start_date"] = start_d
        params["end_date"] = end_d
    if plan.group_by_table and plan.group_by_column:
        gbt, gbc = plan.group_by_table, plan.group_by_column
        select_clause = f'"{gbt}".{gbc} AS group_key, COUNT(*) AS cnt'
        from_clause = f'"{plan.tables[0]}"'
        for j in plan.joins:
            if len(j) != 4:
                continue
            ft, tt, fc, tc = j[0], j[1], j[2], j[3]
            from_clause += f' JOIN "{tt}" ON "{ft}".{fc} = "{tt}".{tc}'
        group_clause = f' GROUP BY "{gbt}".{gbc}'
        order_clause = " ORDER BY cnt DESC"
        where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
        sql = f"SELECT {select_clause} FROM {from_clause}{where_sql}{group_clause}{order_clause} LIMIT :limit"
        params["limit"] = plan.limit
        return sql, params
    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
    sql = f"SELECT {select_clause} FROM {from_clause}{where_sql} LIMIT :limit"
    params["limit"] = plan.limit
    return sql, params
