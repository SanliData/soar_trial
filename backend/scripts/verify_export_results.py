***REMOVED***!/usr/bin/env python3
"""
RESULTS EXPORT – VERIFICATION SCRIPT (TEST & PROOF MODE)

Run with a REAL plan_id that has cached results (min 5 SOAR leads).
No mock data. Produces evidence report: PASS/FAIL per test.

Usage:
  PLAN_ID=<uuid> python scripts/verify_export_results.py
  python scripts/verify_export_results.py <plan_id>

  Optional: BASE_URL=http://localhost:8000 (default)
"""
from __future__ import annotations

import csv
import io
import os
import sys
import zipfile
from typing import Any

try:
    import requests
except ImportError:
    print("FAIL: install requests: pip install requests")
    sys.exit(2)

***REMOVED*** Protocol required columns
LINKEDIN_REQUIRED = [
    "Company Name",
    "Company Domain",
    "City",
    "Country",
    "Company Size",
    "Industry",
    "Job Function",
]
GOOGLE_REQUIRED = [
    "Business Name",
    "Latitude",
    "Longitude",
    "City",
    "Country",
    "Keyword Intent",
]
ZIP_REQUIRED_NAMES = {"linkedin_ads.csv", "google_ads.csv", "campaign_setup.txt"}
CAMPAIGN_SETUP_MUST_CONTAIN = [
    "WHERE TO UPLOAD",
    "linkedin_ads.csv",
    "google_ads.csv",
    "LinkedIn",
    "Google",
]


def main() -> None:
    plan_id = os.environ.get("PLAN_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
    base_url = (os.environ.get("BASE_URL") or "http://localhost:8000").rstrip("/")

    if not plan_id:
        print("FAIL: PLAN_ID required (env or argument). Use a real plan with cached results.")
        sys.exit(1)

    report: dict[str, str] = {}
    evidence: dict[str, Any] = {}

    ***REMOVED*** --- TEST 1: LinkedIn Ads export ---
    try:
        r = requests.post(
            f"{base_url}/api/export/results",
            json={"format": "linkedin_ads", "query_id": plan_id, "language": "en"},
            timeout=30,
        )
        if r.status_code != 200:
            report["ui_linkedin_export"] = "FAIL"
            evidence["linkedin_status"] = r.status_code
            evidence["linkedin_detail"] = (getattr(r, "text", "") or "")[:500]
            if r.status_code == 404:
                evidence["linkedin_reason"] = "No cached results for this plan_id (404)"
        else:
            content = r.content
            if len(content) == 0:
                report["ui_linkedin_export"] = "FAIL"
                evidence["linkedin_reason"] = "file size 0"
            else:
                report["ui_linkedin_export"] = "PASS"
                evidence["linkedin_size"] = len(content)
                evidence["linkedin_filename"] = (
                    r.headers.get("Content-Disposition") or ""
                ).split("filename=")[-1].strip('"')
    except Exception as e:
        report["ui_linkedin_export"] = "FAIL"
        evidence["linkedin_error"] = str(e)

    ***REMOVED*** --- TEST 2: Google Ads export ---
    try:
        r = requests.post(
            f"{base_url}/api/export/results",
            json={"format": "google_ads", "query_id": plan_id, "language": "en"},
            timeout=30,
        )
        if r.status_code != 200:
            report["ui_google_export"] = "FAIL"
            evidence["google_status"] = r.status_code
        else:
            if len(r.content) == 0:
                report["ui_google_export"] = "FAIL"
                evidence["google_reason"] = "file size 0"
            else:
                report["ui_google_export"] = "PASS"
                evidence["google_size"] = len(r.content)
    except Exception as e:
        report["ui_google_export"] = "FAIL"
        evidence["google_error"] = str(e)

    ***REMOVED*** --- TEST 3: Both Ads ZIP ---
    try:
        r = requests.post(
            f"{base_url}/api/export/results",
            json={"format": "both_ads", "query_id": plan_id, "language": "en"},
            timeout=30,
        )
        if r.status_code != 200:
            report["zip_export"] = "FAIL"
            evidence["zip_status"] = r.status_code
        else:
            raw = r.content
            if len(raw) == 0:
                report["zip_export"] = "FAIL"
                evidence["zip_reason"] = "file size 0"
            else:
                with zipfile.ZipFile(io.BytesIO(raw), "r") as zf:
                    names = set(zf.namelist())
                if names != ZIP_REQUIRED_NAMES:
                    report["zip_export"] = "FAIL"
                    evidence["zip_names"] = sorted(names)
                    evidence["zip_expected"] = sorted(ZIP_REQUIRED_NAMES)
                else:
                    report["zip_export"] = "PASS"
                    evidence["zip_names"] = sorted(names)
    except Exception as e:
        report["zip_export"] = "FAIL"
        evidence["zip_error"] = str(e)

    ***REMOVED*** --- TEST 4: CSV schema (using ZIP content if available) ---
    linkedin_headers: list[str] = []
    google_headers: list[str] = []
    try:
        r = requests.post(
            f"{base_url}/api/export/results",
            json={"format": "both_ads", "query_id": plan_id, "language": "en"},
            timeout=30,
        )
        if r.status_code == 200 and len(r.content) > 0:
            with zipfile.ZipFile(io.BytesIO(r.content), "r") as zf:
                if "linkedin_ads.csv" in zf.namelist():
                    with zf.open("linkedin_ads.csv") as f:
                        text = f.read().decode("utf-8", errors="replace")
                        reader = csv.reader(io.StringIO(text))
                        linkedin_headers = next(reader, [])
                if "google_ads.csv" in zf.namelist():
                    with zf.open("google_ads.csv") as f:
                        text = f.read().decode("utf-8", errors="replace")
                        reader = csv.reader(io.StringIO(text))
                        google_headers = next(reader, [])
    except Exception as e:
        evidence["schema_error"] = str(e)

    missing_li = [h for h in LINKEDIN_REQUIRED if h not in linkedin_headers]
    missing_go = [h for h in GOOGLE_REQUIRED if h not in google_headers]
    if missing_li or missing_go:
        report["csv_schema"] = "FAIL"
        if missing_li:
            evidence["linkedin_missing_columns"] = missing_li
        if missing_go:
            evidence["google_missing_columns"] = missing_go
    else:
        report["csv_schema"] = "PASS"
    evidence["linkedin_headers"] = linkedin_headers
    evidence["google_headers"] = google_headers

    ***REMOVED*** --- TEST 5: Platform compatibility ---
    report["linkedin_ads_upload"] = "NOT_RUN"
    report["google_ads_upload"] = "NOT_RUN"
    evidence["platform_note"] = "Manual: upload CSVs in LinkedIn Ads / Google Ads UI and confirm no Invalid format or Unknown column."

    ***REMOVED*** --- TEST 6: campaign_setup.txt ---
    setup_ok = False
    try:
        r = requests.post(
            f"{base_url}/api/export/results",
            json={"format": "both_ads", "query_id": plan_id, "language": "en"},
            timeout=30,
        )
        if r.status_code == 200 and len(r.content) > 0:
            with zipfile.ZipFile(io.BytesIO(r.content), "r") as zf:
                if "campaign_setup.txt" in zf.namelist():
                    with zf.open("campaign_setup.txt") as f:
                        setup_text = f.read().decode("utf-8", errors="replace")
                    missing = [x for x in CAMPAIGN_SETUP_MUST_CONTAIN if x not in setup_text]
                    if missing or len(setup_text.strip()) < 200:
                        report["campaign_setup_txt"] = "FAIL"
                        evidence["setup_missing"] = missing
                        evidence["setup_len"] = len(setup_text)
                    else:
                        report["campaign_setup_txt"] = "PASS"
                        setup_ok = True
                else:
                    report["campaign_setup_txt"] = "FAIL"
                    evidence["setup_missing_file"] = True
        else:
            report["campaign_setup_txt"] = "FAIL"
            evidence["setup_no_zip"] = True
    except Exception as e:
        report["campaign_setup_txt"] = "FAIL"
        evidence["setup_error"] = str(e)
    if not setup_ok and "campaign_setup_txt" not in report:
        report["campaign_setup_txt"] = "FAIL"

    ***REMOVED*** --- TEST 7: Audit log ---
    report["audit_log"] = "NOT_RUN"
    evidence["audit_note"] = "Check backend logs for: export_results trace_id= run_id= format= query_id= row_count="

    ***REMOVED*** --- Final matrix and verdict ---
    print("\n=== RESULTS EXPORT – VERIFICATION REPORT ===\n")
    print("PLAN_ID:", plan_id)
    print("BASE_URL:", base_url)
    print()
    print("TEST MATRIX:")
    for k, v in report.items():
        print(f"  - {k}: {v}")
    print()
    print("EVIDENCE (sanitized):")
    for k, v in evidence.items():
        if k in ("linkedin_headers", "google_headers") and isinstance(v, list):
            print(f"  - {k}: {v[:12]}...")
        else:
            print(f"  - {k}: {v}")
    print()

    failed = [k for k, v in report.items() if v == "FAIL"]
    not_run = [k for k, v in report.items() if v == "NOT_RUN"]
    passed = [k for k, v in report.items() if v == "PASS"]

    if failed:
        print("OVERALL RESULT: NOT VERIFIED")
        print("FAILED:", ", ".join(failed))
    else:
        if not_run:
            print("OVERALL RESULT: VERIFIED (with manual steps)")
            print("Manual steps:", ", ".join(not_run))
        else:
            print("OVERALL RESULT: VERIFIED WORKING")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
