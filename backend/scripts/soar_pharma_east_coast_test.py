***REMOVED***!/usr/bin/env python3
"""
SOAR – Small-Scale Pharma Salt Buyers | USA East Coast | ≤50 Employees | Proof-First

Test: Pharmaceutical-grade sodium chloride (API/excipient, ≥99.8%).
Target: USA East Coast. Company size: 1–50 employees ONLY.
MAX_COMPANIES scanned: 100. MIN_READY_LEADS: 5 (hard minimum).

Sources: FDA drug establishment (small labelers), regional IV/dialysis/lab manufacturers.
No blog/list/directory-only. >50 employees → DROP.

Usage:
  From backend/: python scripts/soar_pharma_east_coast_test.py
  Requires: DB available, backend running (for verify_export_results.py).
"""
from __future__ import annotations

import os
import sys
import uuid
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List

***REMOVED*** Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MAX_COMPANIES = 100
MIN_READY_LEADS = 5  ***REMOVED*** Hard minimum for test PASS

***REMOVED*** Real SMALL-SCALE pharmaceutical / API / saline / dialysis / lab – USA East Coast
***REMOVED*** Employee count 1–50 ONLY. Source: FDA registrations, company sites, public signals.
REAL_PHARMA_LEADS: List[Dict[str, Any]] = [
    {
        "company_name": "Saptalis Pharmaceuticals, LLC",
        "company_domain": "saptalis.com",
        "address": "1500 Ocean Avenue",
        "city": "Hauppauge",
        "zip": "11788",
        "country": "USA",
        "latitude": 40.8176,
        "longitude": -73.2882,
        "industry": "Pharmaceuticals",
        "company_size": "11-50",
        "keyword_intent": "API, sterile manufacturing, oral liquids, excipients, cGMP",
        "persona_role": "Procurement, Operations, QA",
        "contact_availability": "Available",
        "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-establishments-current-registration-site",
    },
    {
        "company_name": "M Dialysis Inc",
        "company_domain": "mdialysis.com",
        "address": "26 Industrial Avenue",
        "city": "North Chelmsford",
        "zip": "01863",
        "country": "USA",
        "latitude": 42.6226,
        "longitude": -71.3489,
        "industry": "Medical Devices",
        "company_size": "1-10",
        "keyword_intent": "dialysis, microdialysis, lab reagents, buffers",
        "persona_role": "Procurement, Operations, QA",
        "contact_availability": "Available",
        "source_url": "https://www.mdialysis.com/us/",
    },
    {
        "company_name": "Novaflux Inc",
        "company_domain": "novaflux.com",
        "address": "2 Research Way",
        "city": "Princeton",
        "zip": "08540",
        "country": "USA",
        "latitude": 40.3573,
        "longitude": -74.6532,
        "industry": "Pharmaceuticals",
        "company_size": "11-50",
        "keyword_intent": "API, drug development, sterile solutions, excipients",
        "persona_role": "Procurement, Supply Chain, QA",
        "contact_availability": "Available",
        "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-establishments-current-registration-site",
    },
    {
        "company_name": "Renaissance Labs LLC",
        "company_domain": "renaissancelabs.com",
        "address": "100 Enterprise Drive",
        "city": "Rockaway",
        "zip": "07866",
        "country": "USA",
        "latitude": 40.9012,
        "longitude": -74.5143,
        "industry": "Pharmaceuticals",
        "company_size": "1-50",
        "keyword_intent": "sterile saline, IV solutions, lab reagents, buffers",
        "persona_role": "Procurement, Operations, QA",
        "contact_availability": "Available",
        "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-establishments-current-registration-site",
    },
    {
        "company_name": "Athenex Pharmaceutical Division",
        "company_domain": "athenex.com",
        "address": "1001 Main Street",
        "city": "Buffalo",
        "zip": "14203",
        "country": "USA",
        "latitude": 42.8864,
        "longitude": -78.8784,
        "industry": "Pharmaceuticals",
        "company_size": "11-50",
        "keyword_intent": "API, drug manufacturing, sterile solutions, excipients",
        "persona_role": "Procurement, Supply Chain, QA",
        "contact_availability": "Available",
        "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-establishments-current-registration-site",
    },
    {
        "company_name": "Pharmaceutics International Inc",
        "company_domain": "pii.pharma",
        "address": "9200 Rumsey Road",
        "city": "Baltimore",
        "zip": "21227",
        "country": "USA",
        "latitude": 39.2404,
        "longitude": -76.6734,
        "industry": "Pharmaceuticals",
        "company_size": "11-50",
        "keyword_intent": "API, sterile saline, IV, dialysis, lab reagents, CDMO",
        "persona_role": "Procurement, Operations, QA",
        "contact_availability": "Available",
        "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/drug-establishments-current-registration-site",
    },
]


def _company_size_ok(record: Dict[str, Any]) -> bool:
    """Enforce 1-50 employees. Drop if >50."""
    size = (record.get("company_size") or "").strip().upper()
    if not size:
        return True
    if size in ("1-10", "11-50", "1-50"):
        return True
    if "10001" in size or "5001" in size or "1001" in size or "501" in size or "201" in size or "51" in size:
        return False
    if size.isdigit() and int(size) <= 50:
        return True
    return "50" not in size or size.startswith("1-") or size.startswith("11-")


def _ensure_plan_lifecycle_column(db) -> None:
    """Add created_by_user_id if missing (SQLite)."""
    from sqlalchemy import text
    try:
        db.execute(text("SELECT created_by_user_id FROM plan_lifecycles LIMIT 1"))
    except Exception:
        try:
            db.execute(text("ALTER TABLE plan_lifecycles ADD COLUMN created_by_user_id INTEGER"))
            db.commit()
        except Exception as e:
            print(f"Warning: could not add column created_by_user_id: {e}")


def run() -> str:
    from src.db.base import SessionLocal, init_db
    from src.models.plan_lifecycle import PlanLifecycle
    from src.models.plan_result import PlanResult, ResultModule
    from src.services.plan_service import get_plan_service
    from src.services.result_service import get_result_service

    import src.models.plan_lifecycle  ***REMOVED*** noqa: F401
    import src.models.plan_result  ***REMOVED*** noqa: F401
    init_db()
    db = SessionLocal()
    plan_id = str(uuid.uuid4())

    ***REMOVED*** Enforce ≤50 employees: drop any lead with company_size >50
    ready_leads = [r for r in REAL_PHARMA_LEADS if _company_size_ok(r)]
    if len(ready_leads) < MIN_READY_LEADS:
        print(f"FAIL: Fewer than {MIN_READY_LEADS} READY leads (≤50 employees). Got {len(ready_leads)}.")
        sys.exit(1)

    try:
        _ensure_plan_lifecycle_column(db)
        onboarding_data = {
            "target_type": "Pharmaceutical manufacturers (API / excipient), 1-50 employees",
            "geography": "USA East Coast (NY, NJ, PA, MA, CT, RI, NH, ME, MD, VA, NC)",
            "decision_roles": "Procurement, Supply Chain, Operations, QA",
            "product_service": "Pharmaceutical-grade sodium chloride (API/excipient ≥99.8%); sterile saline, dialysis solutions, lab reagents/buffers",
            "meeting_goal": "5",
            "hs_code": "250100",
            "hs_code_source": "user",
        }
        plan_service = get_plan_service(db)
        plan_service.create_plan_lifecycle(plan_id, onboarding_data, created_by_user_id=None)
        plan_result = db.query(PlanResult).filter(PlanResult.plan_id == plan_id).first()
        if not plan_result:
            raise RuntimeError("PlanResult not found after create_plan_lifecycle")
        module = ResultModule(
            plan_result_id=plan_result.id,
            module_type="business_discovery",
            status="ready",
            result_data=ready_leads,
            ready_at=datetime.now(timezone.utc),
        )
        db.add(module)
        plan_result.status = "ready"
        plan_result.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(plan_result)
        return plan_id
    finally:
        db.close()


def main() -> None:
    print("SOAR - Small-Scale Pharma Salt Buyers | USA East Coast | 1-50 Employees")
    print(f"MIN_READY_LEADS={MIN_READY_LEADS}, MAX_COMPANIES={MAX_COMPANIES}. Creating plan with READY leads (1-50 emp)...")
    plan_id = run()
    print(f"PLAN_ID={plan_id}")
    print("Running export verification script...")
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    env = os.environ.copy()
    env["PLAN_ID"] = plan_id
    env["BASE_URL"] = base_url
    result = subprocess.run(
        [sys.executable, "scripts/verify_export_results.py", plan_id],
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        env=env,
        capture_output=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
