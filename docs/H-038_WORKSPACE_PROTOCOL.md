***REMOVED*** H-038 — Workspace Protocol Layer (Foundation)

***REMOVED******REMOVED*** Purpose

Define a **governed** workspace protocol surface: deterministic policies, modular runtime rule buckets, **scoped** operational memory manifests, command and skill registries, and explicit permission plus **isolated subagent scope** metadata. This foundation does **not** implement unrestricted persistent stores, autonomous workspace rewriting, or ungoverned agent spawning.

***REMOVED******REMOVED*** Components

| Module | Responsibility |
|--------|------------------|
| `workspace_policy_registry` | Named policies with scope, execution permissions, memory scope, escalation, audit flags. |
| `runtime_rule_service` | Separate buckets (`domain`, `workflow`, `security`, `evaluation`, `orchestration`) with deterministic merge. |
| `project_memory_service` | Typed memory manifests with caps; **`unrestricted_persistent_memory: false`**. |
| `agent_scope_service` | Subagent tool/domain/memory/escalation boundaries; **`uncontrolled_spawn: false`**. |
| `workspace_command_registry` | Operational commands with scoped execution semantics. |
| `workspace_skill_registry` | Reusable skill packages with explicit activation. |
| `permission_governance_service` | Allowlists, deny rules, memory/domain constraints; **`hidden_execution_permissions: false`**. |
| `workspace_validation_service` | Rejects invalid policies and unsafe metadata flags. |

***REMOVED******REMOVED*** HTTP API

Under `/api/v1/system/workspaces/`:

- `GET /policies`, `/rules`, `/memory`, `/commands`, `/skills`, `/permissions`

Envelope includes `workspace_protocol_foundation: true` and negated flags for unrestricted memory, autonomous workspace mutation, and uncontrolled agent spawning.

***REMOVED******REMOVED*** Explicitly deferred

- Unrestricted persistent memory and cross-tenant omniscience.
- Autonomous workspace mutation and recursive workspace evolution.
- Uncontrolled parallel agent spawning and hidden execution grants.
- Monolithic mega-prompt blobs as the sole runtime contract.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h038_workspace_protocol.py
cd backend && python -m pytest tests/test_workspace_protocol.py tests/test_semantic_capabilities.py -q
```

Optional smoke with `VERIFY_BASE_URL` set to a running backend.
