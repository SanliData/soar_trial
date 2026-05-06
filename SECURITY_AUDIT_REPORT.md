***REMOVED*** Security audit report — Secret exposure & public-safety sanitization

***REMOVED******REMOVED*** Executive summary

This repository previously claimed “sanitized”, but **active secrets were found** in the current working tree and **multiple historical commits** still contain secrets. The repo is **not safe for public GitHub exposure** until history is rewritten and keys are rotated.

***REMOVED******REMOVED*** Findings (high severity)

***REMOVED******REMOVED******REMOVED*** 1) Hardcoded production API keys in frontend + test utilities (CURRENT WORKING TREE)

- **Impact**: Anyone cloning the repo could use the key to access production endpoints; keys were also embedded in static UI pages.
- **Evidence (examples)**:
  - `backend/tests/*` contained `API_KEY = "..."`
  - `backend/src/ui/**/soarb2b_*.html` contained `const API_KEY = '...'`
  - `backend/env.yaml` contained `SOARB2B_API_KEYS: "..."` (deleted)
- **Remediation performed**:
  - Removed `PRODUCTION_API_KEYS_UPDATE.md` (contained real key examples).
  - Deleted `backend/env.yaml`.
  - Updated legacy UI pages to read `api_key` from query string (no hardcoded keys).
  - Updated load/rate-limit/audit test utilities to require env vars (`SOARB2B_API_KEY`) rather than embedding secrets.

***REMOVED******REMOVED******REMOVED*** 2) Git history still contains secrets (PAST COMMITS)

Using `git log -S` and `git grep <commit>` shows historical commits contain:

- SOARB2B API keys
- OpenAI API keys
- Google API keys / OAuth secrets (seen previously in push-protection output)
- Stripe test keys / webhook secrets (seen previously in push-protection output)
- GitHub PAT references (seen previously in push-protection output)

**Example commit IDs found**:

- `9e15619` (and others) contain the older SOARB2B API key in multiple docs/scripts.
- `69bee33` (and others) contain the newer API key and deployment scripts.

***REMOVED******REMOVED*** Remediation plan (required to become public-safe)

***REMOVED******REMOVED******REMOVED*** A) Rotate secrets (mandatory)

All exposed credentials **must be rotated**:

- SOARB2B API keys
- Any OpenAI keys ever committed
- Any Google keys / OAuth client secrets ever committed
- Any Stripe keys/webhook secrets ever committed
- Any GitHub PAT ever committed

***REMOVED******REMOVED******REMOVED*** B) Rewrite git history to remove secrets (mandatory for public repo)

Create a sanitized history rewrite using `git filter-repo`:

- Replace known secrets and secret patterns using `security/filter_repo_replace.txt`.
- Run sensitive data removal mode.

Recommended command (run from a clean clone when possible):

```bash
git filter-repo --sensitive-data-removal --replace-text security/filter_repo_replace.txt --force
```

After rewrite:

- Force push to the public remote (coordinate with collaborators).
- Invalidate old clones; follow `git filter-repo --sdr` guidance.

***REMOVED******REMOVED******REMOVED*** C) Prevent future leaks (mandatory)

Added:

- `.pre-commit-config.yaml` (gitleaks + detect-secrets)
- `.gitleaks.toml`
- repo-wide `.gitignore`
- `.env.example`

***REMOVED******REMOVED*** Remaining risks / TODO

- Generate `.secrets.baseline` (detect-secrets) and enforce in CI.
- Add a CI job to run gitleaks on PRs.
- Audit backend security posture (CORS, admin routes, debug endpoints) and harden.

