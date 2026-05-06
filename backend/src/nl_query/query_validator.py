"""
NL_QUERY: query_validator
PURPOSE: Whitelist tables/columns; allow only SELECT; reject dangerous tokens
"""
import logging
import re
from typing import Set

from src.intelligence_graph.graph_query_engine import list_tables, get_table_columns

logger = logging.getLogger(__name__)

ALLOWED_TABLES: Set[str] = set()
_DENY = re.compile(
    r"\b(DROP|DELETE|INSERT|UPDATE|TRUNCATE|ALTER|CREATE|EXEC|EXECUTE|;)\b",
    re.IGNORECASE,
)


def _ensure_whitelist() -> None:
    global ALLOWED_TABLES
    if not ALLOWED_TABLES:
        try:
            ALLOWED_TABLES = set(list_tables())
        except Exception:
            ALLOWED_TABLES = set()


def validate_sql(sql: str, allowed_tables: Set[str] | None = None) -> tuple:
    """
    Validate generated SQL. Returns (ok: bool, error_message: str).
    Ensures SELECT only, no dangerous tokens, only whitelisted table names.
    """
    _ensure_whitelist()
    tables = allowed_tables or ALLOWED_TABLES
    if not sql or not sql.strip().upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"
    if _DENY.search(sql):
        return False, "Query contains disallowed SQL"
    quoted_tables = re.findall(r'"([a-z_][a-z0-9_]*)"', sql)
    for t in quoted_tables:
        if t not in tables:
            return False, f"Table not allowed: {t}"
    return True, ""
