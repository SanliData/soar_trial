***REMOVED*** Results Export – Verification Report (Test & Proof Mode)

**Rule:** No claims without evidence. "Code exists" or "endpoint returns 200" is not proof. Only real exported files + schema validation count.

---

***REMOVED******REMOVED*** 1. Objective

Verify and prove that SOAR Results Export works for:

1. LinkedIn Ads  
2. Google Ads  
3. Both Ads (ZIP)

If any step fails, report **FAIL** with exact reason. Do not hide failures.

---

***REMOVED******REMOVED*** 2. Preconditions (Mandatory)

- **Real SOAR leads** (minimum 5), having passed:
  - Official source discovery  
  - Website verification  
  - LinkedIn signal analysis  
  - Google Maps location verification  
- No mock data, no hardcoded CSVs, no manual file edits.

---

***REMOVED******REMOVED*** 3. Implemented Alignment with Protocol

***REMOVED******REMOVED******REMOVED*** 3.1 Export router (`backend/src/http/export_results_router.py`)

| Requirement | Implementation |
|-------------|----------------|
| LinkedIn CSV columns | Company Name, Company Domain, City, Country, Company Size, Industry, Job Function, Address, ZIP |
| Google CSV columns | Business Name, Latitude, Longitude, City, Country, Keyword Intent, Address, ZIP |
| ZIP contents | Exactly `linkedin_ads.csv`, `google_ads.csv`, `campaign_setup.txt` (fixed names inside ZIP) |
| UTF-8 | CSV responses and ZIP entries use UTF-8 encoding; `Content-Type: text/csv; charset=utf-8` for CSV |
| campaign_setup.txt | Explains WHERE TO UPLOAD (LinkedIn vs Google), what each file contains, and field meanings |
| Audit | Each export logs: `export_results trace_id=... run_id=... format=... query_id=... row_count=...` |

***REMOVED******REMOVED******REMOVED*** 3.2 Result service (`backend/src/services/result_service.py`)

- `_normalize_record` extended to provide: `company_domain`, `company_size`, `industry`, `country`, `keyword_intent`, plus `latitude`/`longitude` for Google Ads.

***REMOVED******REMOVED******REMOVED*** 3.3 Verification script (`backend/scripts/verify_export_results.py`)

- Calls `POST /api/export/results` for `linkedin_ads`, `google_ads`, `both_ads`.
- Checks: status 200, non‑zero body.
- For ZIP: checks member names are exactly `linkedin_ads.csv`, `google_ads.csv`, `campaign_setup.txt`.
- Validates LinkedIn and Google CSV headers against protocol required columns.
- Validates `campaign_setup.txt` contains required sections (WHERE TO UPLOAD, file names, platform names).
- Outputs **TEST MATRIX** and **OVERALL RESULT** (VERIFIED WORKING / NOT VERIFIED).

---

***REMOVED******REMOVED*** 4. How to Run Verification (Evidence)

1. **Backend** running with latest code (so that `linkedin_ads`, `google_ads`, `both_ads` are accepted).
2. **Real plan_id** that has cached results (e.g. from a completed SOAR run with ≥5 leads).

```bash
cd backend
***REMOVED*** Optional: BASE_URL if not localhost
export BASE_URL=http://localhost:8000
export PLAN_ID=<your_real_plan_id_with_results>
python scripts/verify_export_results.py
***REMOVED*** Or: python scripts/verify_export_results.py <plan_id>
```

3. **Capture evidence:**
   - Console output of the script (TEST MATRIX + EVIDENCE).
   - If all automated tests PASS: download the three exports (LinkedIn CSV, Google CSV, ZIP), keep file sizes and one masked sample row per CSV.
   - **Manual (Test 5):** Upload LinkedIn CSV in LinkedIn Ads UI and Google CSV in Google Ads UI; take screenshots of upload/validation result (no “Invalid format” / “Unknown column”).
   - **Audit (Test 7):** Backend log snippet containing `export_results trace_id= run_id= format= query_id= row_count=`.

---

***REMOVED******REMOVED*** 5. Test Matrix (Fill After Run)

| Test | Status | Evidence |
|------|--------|----------|
| UI → LinkedIn export | ⬜ PASS / FAIL | Downloaded CSV, size, screenshot |
| UI → Google export | ⬜ PASS / FAIL | Downloaded CSV, size |
| ZIP export | ⬜ PASS / FAIL | ZIP contains exactly linkedin_ads.csv, google_ads.csv, campaign_setup.txt |
| CSV schema | ⬜ PASS / FAIL | Required columns present; one masked sample row per CSV |
| LinkedIn Ads upload | ⬜ PASS / FAIL | Screenshot of LinkedIn Ads upload result |
| Google Ads upload | ⬜ PASS / FAIL | Screenshot of Google Ads import result |
| campaign_setup.txt | ⬜ PASS / FAIL | File explains where to upload, LinkedIn vs Google, field meanings |
| Audit logging | ⬜ PASS / FAIL | Log snippet with trace_id, run_id, format |

---

***REMOVED******REMOVED*** 6. Overall Result

- **VERIFIED WORKING** only if all tests above are PASS (and manual steps done with screenshots).
- **NOT VERIFIED** if any test is FAIL; list exact failures and evidence.

**Truth > completion.** A failed test with evidence is a successful verification.

---

***REMOVED******REMOVED*** 7. Run Without Real Plan (Expected)

If you run the script without a valid `PLAN_ID` or with a plan that has no cached results:

- Script exits with: `FAIL: PLAN_ID required` or API returns 404/422.
- With a dummy plan_id and no backend: 422 or connection error; script reports **NOT VERIFIED** and failed tests.

This is correct behavior: no claim of success without real data and successful export.
