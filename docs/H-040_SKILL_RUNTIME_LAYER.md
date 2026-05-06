***REMOVED*** H-040 — Skill Runtime Layer (Foundation)

***REMOVED******REMOVED*** Purpose

Provide a **governed** modular skill runtime: deterministic registries, scoped **dynamic load plans** (metadata only), explicit activation methods, least-privilege permissions, acyclic dependencies with bounded depth semantics, context optimization guidance, and auditable execution traces — without unrestricted skill spawning or monolithic runtime prompts.

***REMOVED******REMOVED*** Components

| Module | Role |
|--------|------|
| `skill_registry_service` | Named skills with tools, activation rules, runtime scope, escalation, dependencies. |
| `dynamic_skill_loader` | `plan_skill_load` — validates intent, scope, permissions, dependency closure. |
| `skill_activation_service` | Supported methods per skill; read-only **active** surface; `describe_activation_trace`. |
| `skill_permission_service` | Tool, memory, domain manifests; `evaluate_skill_permission_gate`. |
| `skill_dependency_service` | Edge export, cycle detection, unsafe inheritance rejection. |
| `skill_context_optimizer` | Per-skill token budget and pruning guidance — no hidden mutation. |
| `skill_execution_trace_service` | Canonical + bounded buffer traces. |
| `skill_validation_service` | Skill name and unsafe metadata validation. |

***REMOVED******REMOVED*** HTTP API

Base: `/api/v1/system/skills`

- `GET /` — registry
- `GET /active` — activation governance view
- `GET /permissions`
- `GET /dependencies`
- `GET /context-optimization`
- `GET /traces`

Envelope negates: unrestricted skill spawning, recursive workflow mutation, hidden tool escalation, uncontrolled inheritance.

***REMOVED******REMOVED*** Explicitly deferred

- Autonomous skill spawning and recursive workflow mutation.
- Giant monolithic runtime instructions as the sole contract.
- Hidden tool escalation and uncontrolled skill inheritance.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h040_skill_runtime.py
cd backend && python -m pytest tests/test_skill_runtime.py tests/test_semantic_capabilities.py -q
```
