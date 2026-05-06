***REMOVED*** Public GitHub exposure checklist

Do **not** make this repo public until all items are complete.

***REMOVED******REMOVED*** Secrets & history

- [ ] Run full secret scan on current tree (regex + entropy).
- [ ] Audit git history for secrets (commits + deleted files).
- [ ] Rewrite history with `git filter-repo --sensitive-data-removal`.
- [ ] Force push rewritten history to the public remote.
- [ ] Rotate all affected secrets (see `SECRET_ROTATION_CHECKLIST.md`).

***REMOVED******REMOVED*** Prevent future leaks

- [ ] Enable GitHub Secret Scanning + Push Protection.
- [ ] Install pre-commit hooks: `pre-commit install`.
- [ ] Add CI check for gitleaks on PRs.
- [ ] Ensure `.env` and all env dumps are ignored.

***REMOVED******REMOVED*** Runtime hardening review

- [ ] Confirm no secrets are returned by any API endpoint.
- [ ] Confirm no secrets are embedded in static HTML/JS.
- [ ] Confirm CORS does not allow `*` with credentials.
- [ ] Confirm debug endpoints are disabled or protected in production.
- [ ] Confirm admin routes require strong auth and are not exposed.

***REMOVED******REMOVED*** Post-public verification

- [ ] Clone repo fresh and re-run secret scans.
- [ ] Run `git log -p` sampling around known-problem dates for regression.
- [ ] Validate that old leaked keys no longer work.

