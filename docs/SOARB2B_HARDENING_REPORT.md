***REMOVED*** SOAR B2B / FinderOS — Strategic Hardening Report

Date: 2026-05-05

***REMOVED******REMOVED*** Scope

This hardening pass implements safe, incremental changes aligned to the Master Backlog and adds a lightweight verification protocol.

Constraints honored:
- Routers were not used to introduce new business logic (pricing fix is frontend-only).
- Existing UI paths remain intact:
  - `/ui/tr/soarb2b_home.html`
  - `/ui/en/soarb2b_home.html`
  - `/health`, `/healthz`, `/readyz`
- No secrets were added.

***REMOVED******REMOVED*** Files changed / added (high-signal list)

***REMOVED******REMOVED******REMOVED*** Added
- `docs/SOARB2B_MASTER_BACKLOG.md`
- `docs/VERIFY_SOARB2B_HARDENING.md`
- `docs/SOARB2B_HARDENING_REPORT.md`
- `scripts/verify_soarb2b_hardening.py`
- `backend/docs/main_book/DOCX_REGEN_NOTE.md`
- `backend/docs/live_book/DOCX_REGEN_NOTE.md`

***REMOVED******REMOVED******REMOVED*** Updated
- `backend/docs/main_book/FinderOS_MainBook_v0.1.html` (added section 16)
- `backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html` (added section 16)
- `backend/src/ui/en/soarb2b_home.html` (pricing fallback + timeout)
- `backend/src/ui/tr/soarb2b_home.html` (pricing fallback + timeout)
- `backend/src/ui/assets/ad-rails.js` (desktop gutters for side rails)

***REMOVED******REMOVED*** Backlog items addressed

This pass **tracks** all items and adds required strategic positioning and verification protocol.

- **Tracked**: A-001 .. G-018 in `docs/SOARB2B_MASTER_BACKLOG.md`
- **Positioning + launch gates**: summarized in MainBook section **16. Strategic Hardening Backlog**
- **Verification protocol**: added to LiveBook section **16. Verification Protocol for Strategic Hardening**

***REMOVED******REMOVED*** Pricing loading investigation (“Loading plans…”)

***REMOVED******REMOVED******REMOVED*** Finding
The homepage pricing grid originally rendered a “Loading plans…” placeholder and relied on JS to replace it.
If JS execution is interrupted (e.g., a script error earlier on the page) or the request hangs, the UI can remain stuck.

Backend endpoint confirmed:
- Frontend calls: `GET /v1/subscriptions/plans`
- Backend router: `subscription_router` is mounted under `router_registry` with prefix `/v1`, and has `@router.get("/plans")` under `/subscriptions`.
  - Effective path: **`/v1/subscriptions/plans`**

***REMOVED******REMOVED******REMOVED*** Fix implemented (safe + non-breaking)
Homepage pricing grid now has **server-rendered fallback cards** (Starter / Growth / Enterprise) so it is never stuck.
The JS loader now:
- uses an **AbortController timeout** (6s)
- checks `response.ok`
- logs **console-only** warnings on failure and keeps the fallback UI

***REMOVED******REMOVED*** Verification commands run

***REMOVED******REMOVED******REMOVED*** Hardening verification

Command:
- `python scripts/verify_soarb2b_hardening.py`

Result:
- **PASS**

***REMOVED******REMOVED******REMOVED*** Pytest (best-effort)

Attempted:
- From repo root: `python -m pytest tests -q` → `tests` directory not found at root
- From `backend/`: `python -m pytest tests -q` → **FAIL (collection error)**

Failure:
- `ImportError: cannot import name 'SupplySource' from 'src.growth_activation.supply_sources'`

This report does **not** claim test success.

***REMOVED******REMOVED*** Unresolved issues / follow-ups

- **Test suite**: `backend/tests` currently fails during collection due to import mismatch. Recommended next step: fix the failing import or align the module exports in `src/growth_activation/supply_sources.py`.
- **DOCX exports**: DOCX files were not edited/regenerated. Notes added:
  - `backend/docs/main_book/DOCX_REGEN_NOTE.md`
  - `backend/docs/live_book/DOCX_REGEN_NOTE.md`

***REMOVED******REMOVED*** Recommended next step

1. Fix `backend/tests` collection error and restore a green baseline.
2. Implement the simplest “Results Hub as primary value surface” navigation emphasis across `/ui/*`.
3. Start addressing C-007/C-008 by surfacing provenance and confidence fields in Results Hub and exports.

