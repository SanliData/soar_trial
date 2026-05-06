"""
CORE: upap/verify
PURPOSE: Verification gate before export. export_verification.json + min_ready_leads. FAIL -> 422.
ENCODING: UTF-8 WITHOUT BOM
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from src.core.upap.policy import get_limits_from_plan, MIN_READY_LEADS_DEFAULT

logger = logging.getLogger(__name__)


def run_verification_gate(
    plan_id: str,
    run_id: str,
    kept_leads: List[Dict[str, Any]],
    drop_reasons_histogram: Dict[str, int],
    plan_params: Dict[str, Any],
    totals_scanned: int,
    evidence_dir: Optional[Path] = None,
) -> Tuple[Literal["PASS", "FAIL"], Dict[str, Any], Optional[Path]]:
    """
    Run verification gate. Build export_verification.json.
    PASS only if: totals_kept >= min_ready_leads and no other block.
    Returns (status, report_dict, path_to_artifact).
    """
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    limits = get_limits_from_plan(plan_params)
    min_ready = limits.get("min_ready_leads") if limits.get("min_ready_leads") is not None else MIN_READY_LEADS_DEFAULT
    totals_kept = len(kept_leads)
    totals_dropped = sum(drop_reasons_histogram.values())

    report = {
        "plan_id": plan_id,
        "run_id": run_id,
        "timestamp": ts,
        "enforced_limits": {
            "company_limit": limits.get("company_limit"),
            "company_size_max": limits.get("company_size_max"),
            "min_ready_leads": min_ready,
            "region_allow_list": limits.get("region_allow_list"),
            "region_deny_list": limits.get("region_deny_list"),
        },
        "totals_scanned": totals_scanned,
        "totals_kept": totals_kept,
        "totals_dropped": totals_dropped,
        "drop_reasons": drop_reasons_histogram,
        "status": "PASS",
        "reason": None,
    }

    if totals_kept < min_ready:
        report["status"] = "FAIL"
        report["reason"] = f"min_ready_leads_not_met: kept={totals_kept}, required={min_ready}"
    elif totals_kept == 0:
        report["status"] = "FAIL"
        report["reason"] = "no_leads_after_filters"

    path = None
    if evidence_dir:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        path = evidence_dir / f"export_verification_{plan_id}_{run_id}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info("UPAP export_verification written path=%s status=%s", path, report["status"])

    return report["status"], report, path
