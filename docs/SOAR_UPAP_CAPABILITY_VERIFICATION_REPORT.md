***REMOVED*** SOAR × UPAP Capability Verification Report

**Date:** 2025-02-08  
**Scope:** SOAR application (this repository) — independent verification against UPAP capability requirements.  
**Rule:** No capability is considered active unless enforced at runtime with evidence. No evidence → NOT APPLIED.

---

***REMOVED******REMOVED*** Reference Documents

- `docs/UPAP_GAP_ANALYSIS.md` — not present in repo (referenced by user).
- `docs/UPAP_AGENT_FEATURE_VERIFICATION_REPORT.md` — not present in repo.
- `docs/CURSOR_UPAP_GAP_IMPLEMENTATION_TALIMAT.md` — not present in repo.

Verification was performed by codebase analysis only.

---

***REMOVED******REMOVED*** PHASE 1 — Verification Table

| UPAP Capability        | SOAR Level | Evidence | Status |
|------------------------|-----------|----------|--------|
| Hard Filters           | PARTIAL   | See §1   | company_limit=100 enforced at plan/query input; company_size_max=50 not enforced; export does not re-validate. |
| Regulated / Simulation | NONE      | See §2   | No regulated domain detection, no simulation_mode, no blocking of real company names. |
| Decision Maker         | NONE      | See §3   | No decision_maker inference call; role/confidence not attached to leads in result_data. |
| Cross-Channel          | NONE      | See §4   | No channel_recommendation computation or storage. |
| Verification Gate      | PARTIAL   | See §5   | Export audit (trace_id, run_id) exists; no export_verification.json or PASS gate before success. |
| Audit                  | PARTIAL   | See §6   | trace_id/run_id set and logged on export; no UPAP calls to propagate to. |

**SOAR Level definitions:**
- **NONE:** Not present in codebase.
- **PARTIAL:** Exists but not fully enforced / no runtime gate / no evidence artifact.
- **ENFORCED:** Runtime gate + explicit FAIL/PASS + evidence artifact (json/log/output).

---

***REMOVED******REMOVED*** Detailed Evidence by Capability

***REMOVED******REMOVED******REMOVED*** 1. Hard Filters (Mandatory)

**UPAP expectation:** `company_size_max = 50`, `company_limit = 100`; validated **before** lead is accepted/exported; SOAR blocks execution on FAIL.

**Findings:**

| Check | Result | Evidence |
|-------|--------|----------|
| company_limit = 100 | **Enforced at input only** | `backend/src/core/query_limits.py`: `MAX_RESULTS_PER_QUERY = 100`. `b2b_api_router.py` (create plan): `normalized_max_results = min(request.max_results, MAX_RESULTS_PER_QUERY)` (line ~317). Quote token validation uses this cap. |
| company_limit at export | **Not enforced** | `result_service.get_export_rows()` returns all deduped rows from result modules; no cap at 100. Export can return >100 rows if data was stored via other path. |
| company_size_max = 50 | **Not enforced** | No validation of `company_size` ≤ 50 anywhere. `result_service._normalize_record()` reads `company_size` from records but does not filter or reject. No gate before lead accept/export. |

**Code paths:**
- Enforcing 100 at plan/query: `backend/src/http/v1/b2b_api_router.py` (normalize max_results, quote token), `backend/src/core/query_limits.py` (`enforce_query_limit`, `MAX_RESULTS_PER_QUERY`).
- Export path (no hard filter): `backend/src/http/export_results_router.py` → `result_service.get_export_rows(query_id)` → no company_limit nor company_size_max check.

**Example FAIL response:** SOAR does not return a dedicated FAIL for “company_size > 50” or “company_limit exceeded at export”; it would succeed with whatever rows are cached.

**Verdict:** **PARTIAL** — company_limit=100 enforced at plan/query creation; company_size_max=50 absent; export does not re-validate limits.

---

***REMOVED******REMOVED******REMOVED*** 2. Regulated / Simulation Mode

**UPAP expectation:** SOAR detects regulated domain; forces `simulation_mode` for regulated data; blocks real company names in simulation.

**Findings:**

- **Grep:** No occurrences of `simulation_mode`, `regulated`, or `regulated_domain` in `backend/src`.
- No code path for regulated domain detection or simulation-only behavior.
- No payload or storage of `simulation_mode`; no blocking of real company names.

**Verdict:** **NONE.**

---

***REMOVED******REMOVED******REMOVED*** 3. Decision Maker Resolution

**UPAP expectation:** SOAR calls decision_maker inference; role + confidence attached to leads (DB / result_data).

**Findings:**

- **decision_maker** appears only in: case library JSON (`decision_maker_coverage`), `usage_billing_service` (pricing event type `decision_maker_match`), `usage_tracking` model (`decision_maker_match_count`). No inference **call** or **resolution** step.
- `result_service._normalize_record()` maps `persona_role` / `role` / `decision_role` from existing record keys but does not call any decision_maker inference; no `confidence` field added to normalized records or result_data.

**Code path:** Lead data flows from `ResultModule.result_data` → `_extract_rows_from_module` → `_normalize_record`. No decision_maker inference in this path.

**Verdict:** **NONE.**

---

***REMOVED******REMOVED******REMOVED*** 4. Cross-Channel Recommendation

**UPAP expectation:** SOAR computes `channel_recommendation`; deterministic and stored.

**Findings:**

- **Grep:** No `channel_recommendation` or `cross.channel` in `backend/src`.
- Exports (CSV/PDF/LinkedIn/Google Ads) do not include or derive channel recommendation; no storage in plan_result or result_data.

**Verdict:** **NONE.**

---

***REMOVED******REMOVED******REMOVED*** 5. Verification / Evidence Gate

**UPAP expectation:** SOAR requires `export_verification.json` (or equivalent); PASS required before “success” is returned.

**Findings:**

- No `export_verification.json` read or written in export flow. No verification gate that blocks success until PASS.
- `docs/RESULTS_EXPORT_VERIFICATION_REPORT.md` describes a **verification script** and **audit logging**; it does not describe a runtime gate that prevents export success without verification PASS.
- Export success: `export_results_router` returns CSV/PDF/stream if `get_export_rows(query_id)` returns rows; no check for a verification artifact.

**Evidence of existing audit:**  
`backend/src/http/export_results_router.py`: `trace_id`, `run_id` set and logged (e.g. `export_results trace_id=... run_id=... format=... query_id=... row_count=...`). This is audit trail only, not a verification gate.

**Verdict:** **PARTIAL** — audit/trace present; no mandatory verification PASS gate before success.

---

***REMOVED******REMOVED******REMOVED*** 6. Audit (Trace / Run)

**UPAP expectation:** SOAR propagates `trace_id` / `run_id` into UPAP calls; SOAR actions auditable.

**Findings:**

- **trace_id / run_id:** Set in `export_results_router`: `trace_id = getattr(http_request.state, "request_id", None) or str(uuid.uuid4())`, `run_id = str(uuid.uuid4())`. Logged: `logger.info("export_results trace_id=%s run_id=%s ...", trace_id, run_id, ...)`.
- **Request ID:** `RequestIDMiddleware` sets `request.state.request_id` (from `X-Request-ID` or generated UUID); used in structured logging.
- **UPAP calls:** No UPAP client or outbound UPAP API calls in the repository; no place to “propagate” trace_id/run_id to UPAP.

**Verdict:** **PARTIAL** — trace_id/run_id present and logged for export; no UPAP integration to propagate to.

---

***REMOVED******REMOVED*** Summary Table (Phase 1)

| Capability       | Level   |
|------------------|---------|
| Hard Filters     | PARTIAL |
| Simulation Mode  | NONE    |
| Decision Maker   | NONE    |
| Cross-Channel    | NONE    |
| Verification Gate| PARTIAL |
| Audit            | PARTIAL |

---

***REMOVED******REMOVED*** Final Verdict (Phase 1)

**SOAR is NOT UPAP-COMPLIANT.**

- Mandatory capabilities are not all **ENFORCED**.
- Gaps: **company_size_max=50** and export-time **company_limit** re-check (Hard Filters); **Regulated/Simulation**; **Decision Maker** inference and storage; **Cross-Channel** recommendation; **Verification Gate** (PASS required before success); full **Audit** propagation to UPAP (no UPAP integration present).

---

***REMOVED******REMOVED*** Next: Phase 2 — Gap Closure

Phase 2 will implement enforcement for each NONE/PARTIAL item (within SOAR only): UPAP core functions where applicable, fail-fast on FAIL, and evidence artifacts (reason, limit, trace_id, timestamp). No silent fallback; no “best effort.”

---

***REMOVED******REMOVED*** PHASE 2 — Gap Closure (Implemented)

Implemented enforcement for **Hard Filters** and **Verification Gate** only. Regulated/Simulation, Decision Maker, and Cross-Channel remain NONE.

***REMOVED******REMOVED******REMOVED*** 2.1 Hard Filters — Now ENFORCED at Export

- **New:** `backend/src/core/upap_limits.py` — `COMPANY_SIZE_MAX = 50`, `COMPANY_LIMIT = 100`; `filter_rows_by_upap(rows, trace_id, run_id)` filters by size and caps at 100; returns `(filtered_rows, evidence)`.
- **Modified:** `backend/src/http/export_results_router.py` — After `get_export_rows`, calls `filter_rows_by_upap`; on FAIL (no rows after filter) raises `HTTPException(400, detail={...})` with reason, limit, trace_id, run_id, timestamp. All exports use `filtered_rows`.

**Example FAIL (400):** `detail.error_code`: `UPAP_EXPORT_FAIL`, `detail.reason`: `no_rows_after_upap_filters`, plus `limit`, `company_size_max`, `trace_id`, `run_id`, `timestamp`, `rows_before`, `rows_after`, `rejected_size_count`.

**Test:** `backend/tests/test_upap_limits.py` (13 tests).

***REMOVED******REMOVED******REMOVED*** 2.2 Verification Gate — Now ENFORCED

- **Modified:** `export_results_router` — `_write_export_verification_artifact(...)` writes `data/exports/evidence/export_verification_{query_id}_{run_id}.json` with status, reason, limit, trace_id, run_id, timestamp. Called only after UPAP filter PASS, before returning success (PASS required before success).

***REMOVED******REMOVED******REMOVED*** 2.3 Audit

trace_id/run_id in FAIL response body and in every export_verification.json artifact. No UPAP service in-repo to propagate to.

---

***REMOVED******REMOVED*** Before / After Comparison

| Capability        | Before   | After (Phase 2)   |
|-------------------|----------|-------------------|
| Hard Filters       | PARTIAL  | **ENFORCED**      |
| Simulation Mode   | NONE     | NONE              |
| Decision Maker     | NONE     | NONE              |
| Cross-Channel      | NONE     | NONE              |
| Verification Gate | PARTIAL  | **ENFORCED**      |
| Audit              | PARTIAL  | PARTIAL           |

---

***REMOVED******REMOVED*** Final Statement

**SOAR is NOT UPAP-COMPLIANT (missing items listed).**

- **Hard Filters** and **Verification Gate** are **ENFORCED** (runtime gate, FAIL on violation, evidence artifact).
- Still missing: **Regulated/Simulation**, **Decision Maker**, **Cross-Channel**; **Audit** has no UPAP to propagate to.

Evidence: `backend/src/core/upap_limits.py`, `backend/src/http/export_results_router.py`, `backend/tests/test_upap_limits.py`, `data/exports/evidence/export_verification_*.json`.

End of report.
