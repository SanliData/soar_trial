***REMOVED*** H-036 — Evolution Governance (Foundation)

***REMOVED******REMOVED*** Purpose

Provide a **sandboxed, governance-gated** foundation for self-optimization ideas: proposals, isolated evaluation, rollback checks, workflow/prompt **simulation**, and auditable evolution traces. This layer does **not** deploy changes to production or rewrite runtime behaviour.

***REMOVED******REMOVED*** Principles

- **Deterministic** metadata and score tables; no network side effects in this foundation.
- **Explainable** proposal records and structured sandbox results.
- **Auditable** trace shapes (canonical + optional bounded buffer).
- **Reversible** semantics: every proposal advertises `rollback_available`; rollback governance checks are explicit.
- **Governance-gated** policy slots: `governance_approval_required` and `autonomous_deploy: false` in policy evolution.

***REMOVED******REMOVED*** Components

| Module | Role |
|--------|------|
| `mutation_proposal_service` | Static registry of typed proposals (`workflow_optimization`, `prompt_optimization`, `retry_policy_update`, `loop_detection_update`, `orchestration_tuning`). |
| `sandbox_evaluation_service` | Deterministic score vectors per proposal type; bundles workflow simulation and optional prompt comparison. |
| `rollback_governance_service` | Rollback readiness from deployment state, approval, and trace storage flags. |
| `evolution_trace_service` | Canonical exemplars + bounded optional buffer. |
| `workflow_mutation_service` | Named scenario simulations only (retry reduction, loop detection, subagent limits, context compression). |
| `prompt_mutation_service` | Static comparison of labeled profiles — no prompt rewriting. |
| `policy_evolution_service` | Declarative policy *slots* for orchestration improvements — proposals only. |
| `evolution_validation_service` | Rejects production deploy via API and unsafe mutation metadata flags. |

***REMOVED******REMOVED*** HTTP API

Mounted under `/api/v1` (see router). Response envelope includes:

- `evolution_governance_foundation: true`
- `unrestricted_runtime_self_modification: false`
- `autonomous_production_mutation: false`
- `recursive_evolution_loops: false`

***REMOVED******REMOVED*** Explicitly deferred

- Autonomous runtime mutation and production rewriting.
- Recursive self-healing or unbounded evolution loops.
- Unrestricted self-modification or self-expanding workflow graphs.
- Delegated autonomous orchestration evolution without human governance.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h036_evolution_governance.py
cd backend && python -m pytest tests/test_evolution_governance.py -q
```

Optional live smoke with a running backend:

```bash
set VERIFY_BASE_URL=http://127.0.0.1:8000
python scripts/verify_h036_evolution_governance.py
```
