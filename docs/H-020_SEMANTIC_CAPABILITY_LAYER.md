***REMOVED*** H-020 — Semantic Capability Layer / Agent-Native Backend Foundation

**Status**: Foundation Implemented (controlled, deterministic metadata only)

***REMOVED******REMOVED*** Problem this solves

- **Hallucinated orchestration**: Planner models invent HTTP flows, payloads, side effects, and auth expectations that the backend does not provide.
- **Missing backend semantics**: Risk, sensitivity, destructive impact, refresh semantics, idempotency, and allowed roles historically lived only in human docs.
- **Unsafe agent execution**: Without explicit manifests, tooling may chain calls that violate least privilege or customer governance.

SOAR B2B needs a machine-readable—but **human-curated**—capability ledger that complements OpenAPI schemas with orchestration-facing semantics.

***REMOVED******REMOVED*** Why this matters for SOAR B2B

Commercial Intelligence workloads (`automation_engine`, graph intelligence surfaces, deterministic generative widgets, opportunity scoring, and future multi-agent tooling) assume reliable contracts:

- Exposure and onboarding flows mutate customer-facing state—metadata must shout when **human approval** is required before automation can proceed safely.
- Read-only analytic paths can be flagged `orchestration_safe=true` while still documenting **risk** and sensitive fields touched.
- Controlled generative UI (H-019) complements this layer: manifests describe **where** planners may suggest UI payloads without granting runtime JS privileges.

***REMOVED******REMOVED*** What is intentionally NOT implemented

- No autonomous AI execution loop, no adaptive permissions, no self-editing manifests.
- No reflection-based runtime discovery beyond the deterministic registry curated in code review.
- No embedding of `.env`, connection strings, private keys, or internal tokens inside exports.
- Unrestricted orchestration planners that bypass security reviews remain out of scope.

***REMOVED******REMOVED*** Implemented components

Package `backend/src/semantic_capabilities/`:

- `capability_schema.py` — Canonical Pydantic model with forbidden extras.
- `capability_registry.py` — Checked-in deterministic entries for prioritized routes.
- `capability_validation.py` — Structural + orchestration invariant checks plus export secret sniffing guards.
- `capability_export_service.py` — Builds sanitized JSON (`system`, `version`, `capabilities`).
- Loader + exporter consumed by routers only through services.

Router `backend/src/http/v1/semantic_capability_router.py`:

- Thin FastAPI façade calling `build_capabilities_catalog()`.

***REMOVED******REMOVED*** Public endpoint

```
GET /api/v1/system/capabilities
```

Response shape:

```json
{
  "system": "FinderOS / SOAR B2B",
  "version": "<semver from FINDEROS_VERSION>",
  "capabilities": [ ... ]
}
```

***REMOVED******REMOVED*** Security principles

| Principle | Enforcement |
|-----------|-------------|
| Deterministic metadata | Registry authored in-repo; loaders validate uniqueness + enums at import time |
| Explicit risk tiers | Allowed values: `low`, `medium`, `high`, `critical` |
| Least privilege | `auth_required`, `allowed_roles`, and orchestration booleans annotated explicitly |
| Human approval semantics | Exposure creation, onboarding plan creation, and visit-route artefacts require `human_approval_required=true` |
| Orchestration boundaries | `orchestration_safe` never pairs with undocumented destructive deletes |
| No secret leakage | Exporter forbids stray env blobs in payload (pattern-based audit guard) |

**AI systems must not assume implicit execution authority.** Manifest booleans advertise intent; callers still authenticate, honor rate limits, and respect policy engines.

***REMOVED******REMOVED*** Governance & expansion

Adding capabilities requires:

1. Registry entry reviewed by engineers + security/contact for customer impact.
2. Validation rules updated if introducing new semantics (destructive deletes, outbound messaging, asynchronous jobs).
3. LiveBook/MainBook verification snippets adjusted when materially changing risk posture.

***REMOVED******REMOVED*** Verification

Automated checklist: `python scripts/verify_h020_semantic_layer.py`.

Optional live probes: export `VERIFY_BASE_URL` before running the script to hit the HTTP endpoint remotely.
