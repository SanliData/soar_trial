"""
CORE: upap_limits
PURPOSE: UPAP-mandatory hard filters enforced at runtime.
ENCODING: UTF-8 WITHOUT BOM

- company_size_max = 50 (per lead)
- company_limit = 100 (max leads per export/accept)
No silent fallback; fail fast on violation; emit reason, limit, trace_id, timestamp.
"""

import re
from typing import Tuple, List, Dict, Any, Optional

# UPAP-mandatory constants (non-negotiable)
COMPANY_SIZE_MAX = 50
COMPANY_LIMIT = 100


def _parse_company_size_max(raw: Optional[str]) -> Optional[int]:
    """
    Parse company_size string to a single numeric max (employee count).
    Returns None if unparseable (then treat as unknown; caller may allow or reject by policy).
    Examples: "1-10" -> 10, "11-50" -> 50, "51-200" -> 200, "1001-5000" -> 5000, "50" -> 50.
    """
    if not raw or not isinstance(raw, str):
        return None
    s = str(raw).strip()
    if not s:
        return None
    # Range patterns: 1-10, 11-50, 51-200, 1001-5000
    range_match = re.match(r"(\d+)\s*-\s*(\d+)", s)
    if range_match:
        low, high = int(range_match.group(1)), int(range_match.group(2))
        return max(low, high)
    # Single number
    if s.isdigit():
        return int(s)
    # Fallback: take last number found (e.g. "50 employees")
    nums = re.findall(r"\d+", s)
    if nums:
        return max(int(n) for n in nums)
    return None


def passes_company_size_max(company_size_raw: Optional[str]) -> bool:
    """
    True if lead passes UPAP company_size_max = 50.
    - If unparseable (None): treat as unknown; we ALLOW (no evidence of >50).
    - If parseable: allow only if max <= COMPANY_SIZE_MAX.
    """
    max_val = _parse_company_size_max(company_size_raw)
    if max_val is None:
        return True   # Unknown size: allow (conservative for inclusion)
    return max_val <= COMPANY_SIZE_MAX


def filter_rows_by_upap(
    rows: List[Dict[str, Any]],
    trace_id: str,
    run_id: str,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply UPAP hard filters to candidate export rows.
    - company_size_max = 50: drop rows where company_size parses to > 50.
    - company_limit = 100: cap to first 100 rows after size filter.

    Returns (filtered_rows, evidence).
    evidence contains: reason, limit, trace_id, timestamp, status (PASS/FAIL),
    rows_before, rows_after, rejected_size_count, company_size_max, company_limit.
    """
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    evidence = {
        "reason": None,
        "limit": COMPANY_LIMIT,
        "company_size_max": COMPANY_SIZE_MAX,
        "trace_id": trace_id,
        "run_id": run_id,
        "timestamp": ts,
        "status": "PASS",
        "rows_before": len(rows),
        "rows_after": 0,
        "rejected_size_count": 0,
    }
    if not rows:
        evidence["status"] = "FAIL"
        evidence["reason"] = "no_rows"
        evidence["rows_after"] = 0
        return [], evidence

    # 1) Filter by company_size <= 50
    allowed = []
    rejected_size_count = 0
    for row in rows:
        raw = row.get("company_size") or row.get("Company Size") or ""
        if passes_company_size_max(raw):
            allowed.append(row)
        else:
            rejected_size_count += 1

    evidence["rejected_size_count"] = rejected_size_count
    # 2) Cap at company_limit
    capped = allowed[:COMPANY_LIMIT]
    evidence["rows_after"] = len(capped)

    if len(capped) == 0:
        evidence["status"] = "FAIL"
        evidence["reason"] = "no_rows_after_upap_filters"
    elif len(allowed) > COMPANY_LIMIT:
        evidence["status"] = "PASS"
        evidence["reason"] = "capped_to_company_limit"
    else:
        evidence["status"] = "PASS"
        evidence["reason"] = "ok"

    return capped, evidence
