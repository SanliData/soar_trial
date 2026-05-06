"""
CORE: upap/evidence
PURPOSE: Write UPAP evidence artifact before successful EXPORT response.
ENCODING: UTF-8 WITHOUT BOM

Path: data/exports/evidence/upap_evidence_{query_id}_{run_id}.json
Success response ONLY after evidence is written.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Same base as export router
EVIDENCE_BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "exports" / "evidence"


def write_upap_evidence(
    query_id: str,
    run_id: str,
    evidence: Dict[str, Any],
    evidence_dir: Optional[Path] = None,
) -> Path:
    """
    Write upap_evidence_{query_id}_{run_id}.json.
    evidence MUST contain: trace_id, run_id, query_id, timestamp, regulated_domain,
    simulation_mode, limits, rows_before, rows_after, rejected_counts,
    decision_maker_summary, channel_summary, status, reason (if FAIL).
    """
    evidence_dir = evidence_dir or EVIDENCE_BASE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"upap_evidence_{query_id}_{run_id}.json"
    path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    logger.info("UPAP evidence written path=%s status=%s", path, evidence.get("status"))
    return path
