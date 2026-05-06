***REMOVED*** SOAR UPAP “Kas” Integration — Summary

***REMOVED******REMOVED*** What is enforced

UPAP is implemented as a **capability layer (“kas”)** inside the SOAR backend. All critical export paths call a single entry point; there is **no silent fallback** and **no success without evidence**.

***REMOVED******REMOVED******REMOVED*** Gates enforced

| Gate | File | Behaviour | Evidence / audit |
|------|------|-----------|------------------|
| **A) Regulated / simulation** | `backend/src/core/upap/regulated.py` | If `regulated_domain` and `simulation_mode` not true → FAIL. If regulated + simulation and real company name detected → FAIL. | `regulated_domain`, `simulation_mode`, `blocked_reason` in evidence; `upap_gate_pass` / `upap_gate_fail` emitted. |
| **B) Hard filters** | `backend/src/core/upap_limits.py` (used from gates) | `company_size_max=50`, `company_limit=100` applied at EXPORT. Zero rows after filter → FAIL. | `limits`, `rows_before`/`rows_after`, `rejected_counts.size` in evidence; audit event. |
| **C) Decision maker** | `backend/src/core/upap/decision_maker.py` | Deterministic `infer_role(title, dept, keyword_intent)` → role ∈ {Procurement, QA, Ops}, confidence ∈ [0,1]. Missing or invalid role → FAIL. | `decision_maker_role`, `decision_confidence_score` on each lead; `decision_maker_summary` in evidence. |
| **D) Cross-channel** | `backend/src/core/upap/cross_channel.py` | Deterministic `recommend(...)` → `channel_recommendation` (linkedin_only / google_only / both_with_sequence), `channel_rule_id`. Missing or invalid → FAIL. | `channel_recommendation`, `channel_rule_id` on each lead; `channel_summary` in evidence. |
| **E) Verification** | `backend/src/core/upap/evidence.py` + `gates.py` | Before any successful EXPORT response, write `data/exports/evidence/upap_evidence_{query_id}_{run_id}.json`. Success only after file is written. | Evidence file contains trace_id, run_id, query_id, timestamp, all gate outputs, status, reason. |
| **F) Audit** | `backend/src/core/upap/audit.py` | On every gate outcome emit `upap_gate_pass` or `upap_gate_fail` with trace_id, run_id, query_id, gate_name, status, reason, limits, timestamp. | Logged with structured payload (`extra={"upap_audit": payload}`). |

***REMOVED******REMOVED******REMOVED*** Single entry point

- **File:** `backend/src/core/upap/gates.py`  
- **Function:** `run_upap_gates(stage, trace_id, run_id, query_id, query_params, leads) -> (leads_filtered, upap_evidence, gate_status)`  
- **Stages:** `INGEST`, `ENRICH`, `EXPORT`.  
- **Fail-fast:** Any gate FAIL → immediate return with `gate_status == "FAIL"`; no success response.

***REMOVED******REMOVED******REMOVED*** Integration

- **Export:** `POST /api/export/results` calls `run_upap_gates(stage="EXPORT", ...)` with `query_params` from plan `onboarding_data`. On FAIL → HTTP 400 with body containing `trace_id`, `run_id`, `reason`, and related evidence fields. On PASS, evidence file is written then the export response is returned.
- **Ingest / enrich:** Call sites should call `run_upap_gates(stage="INGEST"` or `"ENRICH", ...)` where leads are produced; same fail-fast behaviour applies.

***REMOVED******REMOVED*** What evidence proves enforcement

1. **Evidence file:** Every successful EXPORT writes `upap_evidence_{query_id}_{run_id}.json` under `data/exports/evidence/` with:
   - `trace_id`, `run_id`, `query_id`, `timestamp`
   - `regulated_domain`, `simulation_mode`, `blocked_reason`
   - `limits` (company_size_max, company_limit)
   - `rows_before`, `rows_after`, `rejected_counts`
   - `decision_maker_summary`, `channel_summary`
   - `status`: `PASS` | `FAIL`, and `reason` when FAIL

2. **Audit events:** Each gate outcome is emitted as `upap_gate_pass` or `upap_gate_fail` with full payload (trace_id, run_id, query_id, gate_name, status, reason, limits, timestamp), so every PASS/FAIL is auditable.

3. **Tests:** `backend/tests/core/test_upap_gates.py` (and existing `test_upap_limits.py`) cover:
   - Regulated + no simulation → FAIL  
   - Regulated + real company name → FAIL  
   - Missing or invalid decision maker → FAIL  
   - Missing or invalid channel recommendation → FAIL  
   - PASS path writes evidence file before response  
   - Hard filters (e.g. all rows over 50 → 0 rows → FAIL)

***REMOVED******REMOVED*** Example evidence

- **PASS:** `docs/upap_evidence_examples/upap_evidence_PASS_example.json`  
- **FAIL:** `docs/upap_evidence_examples/upap_evidence_FAIL_example.json`

***REMOVED******REMOVED*** Compliance statement

**Do not claim “UPAP-compliant” unless all gates above are enforced and evidence is written.** In this implementation, all listed gates are enforced in code, evidence is written on successful EXPORT, and audit events are emitted for every gate outcome.
