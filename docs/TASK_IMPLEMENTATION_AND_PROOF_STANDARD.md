***REMOVED*** Task implementation and proof standard (mandatory)

This document is the canonical checklist for substantive FinderOS / SOAR B2B work. Automated agents must follow `.cursor/rules/ta<REDACTED_OPENAI_API_KEY>.mdc`; this file is for humans browsing `docs/`.

***REMOVED******REMOVED*** 1. MainBook

- Edit: `backend/docs/main_book/FinderOS_MainBook_v0.1.html`
- If DOCX exists: update it safely **or** add a prominent note that **DOCX regeneration is required from HTML/source** (`backend/docs/main_book/DOCX_REGEN_NOTE.md`).

***REMOVED******REMOVED*** 2. LiveBook

- Edit: `backend/docs/live_book/FinderOS_LiveBook_2025-12-13.html`
- Same DOCX rule: `backend/docs/live_book/DOCX_REGEN_NOTE.md`

***REMOVED******REMOVED*** 3. Master backlog

- Edit: `docs/SOARB2B_MASTER_BACKLOG.md`
- Align status, verification method, and dates with reality.

***REMOVED******REMOVED*** 4. Implementation proof report

Create or update: `docs/<TASK_ID>_IMPLEMENTATION_PROOF.md`

Required sections (or equivalent headings):

| Section | Content |
|--------|---------|
| Files changed | Paths (created/modified/removed if any) |
| Implementation summary | What behaviour changed |
| MainBook section | Heading(s) touched |
| LiveBook section | Heading(s) touched |
| Backlog status | What was updated |
| Verification commands | Exact commands executed |
| Test results | `pytest`/other counts or “N/A” with reason |
| PASS/FAIL | Single explicit verdict |
| Unresolved issues | Open risks or deps |
| Next recommended step | One concrete follow-on |

Do **not** mark PASS unless checks actually passed or limitations are spelled out honestly.

***REMOVED******REMOVED*** 5. Verification script

When automation applies:

- Path: `scripts/verify_<task_slug>.py`
- Runner must execute it and paste exit status into proof.

Optional live/API checks: honour `VERIFY_BASE_URL` patterns used elsewhere.

***REMOVED******REMOVED*** 6. Tests

- Run relevant scoped `pytest` from `backend/` and record stdout summary in proof.

***REMOVED******REMOVED*** 7. Completion rule

Declare success only when code + docs + proof + verification (per task scope) are consistent. Otherwise:

> **Implementation incomplete because:** …

