"""
NL_QUERY: response_formatter
PURPOSE: Turn DB rows into result list and optional summary
"""
import logging
from typing import Any, List

logger = logging.getLogger(__name__)


def format_response(rows: List[Any], summary: str = "") -> dict:
    """Return { result: list of dicts, summary: str }."""
    if not rows:
        return {"result": [], "summary": summary or "No data found."}
    out = []
    for row in rows:
        if hasattr(row, "_mapping"):
            out.append(dict(row._mapping))
        elif hasattr(row, "_asdict"):
            out.append(row._asdict())
        elif isinstance(row, dict):
            out.append(row)
        else:
            out.append({"value": row})
    return {"result": out, "summary": summary or f"Returned {len(out)} row(s)."}
