***REMOVED*** H-030 — Backend Context Engineering & Structured Runtime Metadata Layer

**Scope:** Foundation only — curated manifests, deterministic budgeting, no blind infra introspection.

***REMOVED******REMOVED*** Goals

- AI-readable **structured runtime metadata** (subsystem flags, version, capability counts).
- **Capability summaries** first (`depth=summary`), optional **`depth=full`** for progressive loading.
- **Topology manifest** listing curated routers/domains — not live socket/process enumeration.
- **Orchestration hints** — short deterministic strings derived only from structured fields.
- **Context budgeting** — estimated tokens, prioritised layers, explicit truncation markers.

***REMOVED******REMOVED*** HTTP surface

| Method | Path |
|--------|------|
| GET | `/api/v1/system/runtime/metadata` |
| GET | `/api/v1/system/runtime/capabilities` |
| GET | `/api/v1/system/runtime/topology` |
| GET | `/api/v1/system/runtime/hints` |
| POST | `/api/v1/system/runtime/context-budget` |

Governance envelope keys:

- `runtime_context_foundation=true`
- `autonomous_orchestration_mesh=false`
- `runtime_self_modification=false`

***REMOVED******REMOVED*** Context budgeting

POST body (`ContextBudgetRequest`):

- `estimated_chars` — non-negative bound for estimation.
- `requested_layers` — symbolic layers for prioritisation simulation.
- `large_text_sample` — capped (max 256k chars) — summaries use visible `[CONTEXT_TRUNCATED]` markers.

***REMOVED******REMOVED*** Semantic capabilities (H-020)

`runtime.metadata`, `runtime.capabilities`, `runtime.topology`, `runtime.hints`, `runtime.context_budget` — **orchestration_safe=true**, **destructive_action=false**.

***REMOVED******REMOVED*** Explicit deferrals

- Autonomous orchestration meshes and self-exploring runtime agents.
- Distributed orchestration rewrites and runtime self-modification.
- Uncontrolled context expansion without traces and markers.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h030_runtime_context.py
cd backend && python -m pytest tests/test_runtime_context.py -q
```
