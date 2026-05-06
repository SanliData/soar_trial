***REMOVED*** Secret rotation checklist (required)

This repo has evidence of historical secret exposure. Assume compromise and rotate.

***REMOVED******REMOVED*** 1) SOARB2B API keys

- [ ] Generate new production keys.
- [ ] Update Cloud Run / Secret Manager to new values.
- [ ] Invalidate old keys (server-side denylist / remove from allowlist).
- [ ] Update any clients using the old keys.

***REMOVED******REMOVED*** 2) OpenAI API keys

- [ ] Revoke any keys ever committed.
- [ ] Create new keys with least privilege.
- [ ] Ensure keys exist only in Secret Manager and runtime env.

***REMOVED******REMOVED*** 3) Google credentials

- [ ] Rotate any exposed Google API keys.
- [ ] Rotate OAuth client secret(s) if ever committed.
- [ ] Review allowed origins and redirect URIs.

***REMOVED******REMOVED*** 4) Stripe credentials

- [ ] Rotate webhook signing secret(s).
- [ ] Rotate secret keys (test and live if applicable).
- [ ] Confirm webhook endpoints and signing verification remain correct.

***REMOVED******REMOVED*** 5) GitHub credentials

- [ ] Revoke any exposed GitHub PATs.
- [ ] Prefer fine-grained PATs or GitHub Apps with least privilege.

***REMOVED******REMOVED*** 6) JWT/session secrets

- [ ] Rotate `JWT_SECRET` (forces token invalidation).
- [ ] Ensure cookies/sessions become invalid as expected.

***REMOVED******REMOVED*** Order of operations (recommended)

1. Rotate production API keys and OAuth/AI/payment secrets in providers.
2. Deploy runtime with new secrets.
3. Rewrite git history and force-push sanitized history.
4. Validate no old credentials function.

