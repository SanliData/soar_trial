***REMOVED******REMOVED*** H-045 — Unified Agent Operating System, Federated Retrieval Fabric & REFRAG-Inspired Selective Context Runtime

This is a **governed foundation implementation**. It provides deterministic, explainable, auditable metadata surfaces for:

- **Agent operating system** (registry, roles, fleet visibility, permissions, observability)
- **Natural language control plane** (intent parsing/routing/audit; no execution)
- **Federated retrieval fabric** (connectors, incremental sync metadata, search + lineage)
- **Selective context runtime** (chunk compression, relevance policy, selective expansion, budgets, token pressure routing)

***REMOVED******REMOVED******REMOVED*** Explicitly deferred (non-goals)

- Autonomous self-directed agent swarms.
- Unrestricted natural-language execution.
- Giant RL/relevance training infrastructure.
- Uncontrolled retrieval expansion or live external connector execution.
- Fully autonomous fleet mutation.
- Microservice sprawl or replacement of the current FastAPI modular monolith.

***REMOVED******REMOVED******REMOVED*** Domains

- `backend/src/agent_operating_system/`
  - deterministic agent registry and fleet status
  - role-scoped capabilities and explicit escalation policies
  - permission governance gates (fail closed)
  - observability manifests (no hidden telemetry)

- `backend/src/natural_language_control_plane/`
  - deterministic parsing to intent metadata
  - workflow routing metadata
  - approval classification metadata
  - bounded audit log buffer

- `backend/src/federated_retrieval/`
  - connector registry metadata (no secrets, no live sync required)
  - incremental sync freshness metadata
  - deterministic foundation federated search (mock index) with **required source lineage**
  - retrieval observability metrics

- `backend/src/selective_context_runtime/`
  - chunk compression metadata (lineage preserved)
  - deterministic relevance scoring (REFRAG-inspired; no RL)
  - selective expansion decisions (explainable + budget-bound)
  - explicit retrieval budgets + token pressure routing
  - typed context projections that map H-045 artifacts into H-044 types via tags (no new context types)

***REMOVED******REMOVED******REMOVED*** API surfaces (read-only)

- Agent OS:
  - `GET /api/v1/system/agents`
  - `GET /api/v1/system/agents/roles`
  - `GET /api/v1/system/agents/fleet`
  - `GET /api/v1/system/agents/permissions`
  - `GET /api/v1/system/agents/observability`

- NL control plane:
  - `GET /api/v1/system/nl-control/intents`
  - `GET /api/v1/system/nl-control/approval`
  - `GET /api/v1/system/nl-control/audit`

- Federated retrieval:
  - `GET /api/v1/system/retrieval/connectors`
  - `GET /api/v1/system/retrieval/sync`
  - `GET /api/v1/system/retrieval/search`
  - `GET /api/v1/system/retrieval/lineage`
  - `GET /api/v1/system/retrieval/observability`

- Selective context runtime:
  - `GET /api/v1/system/selective-context/compression`
  - `GET /api/v1/system/selective-context/relevance`
  - `GET /api/v1/system/selective-context/expansion`
  - `GET /api/v1/system/selective-context/token-pressure`
  - `GET /api/v1/system/selective-context/budgets`

***REMOVED******REMOVED******REMOVED*** Demo pages

- `backend/src/ui/en/agent_operating_system_demo.html` (+ `tr/…`)
- `backend/src/ui/en/federated_retrieval_demo.html` (+ `tr/…`)
- `backend/src/ui/en/selective_context_runtime_demo.html` (+ `tr/…`)

