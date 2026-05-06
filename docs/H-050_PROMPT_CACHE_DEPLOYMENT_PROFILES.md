***REMOVED******REMOVED*** H-050 — Prompt Cache Governance, Static/Dynamic Context Discipline & Agent Deployment Profile Layer

This backlog item adds **governed foundation** controls for prompt cache stability and safe agent deployment profiles.

***REMOVED******REMOVED******REMOVED*** Goals

- **Static prefix vs dynamic suffix separation**: stable cacheable prefix, auditable growing suffix
- **Cache breakpoint metadata**: explicit boundaries + explainable invalidation reasons
- **Cache efficiency telemetry**: deterministic ratio + safe divide-by-zero handling
- **Tool schema stability**: detection-only drift signals, cache reset warnings (no mutation)
- **Model session stability**: detection-only model/provider drift, reset required metadata
- **Cache-safe compression**: compression instructions added as suffix; static prefix never rewritten
- **Governed deployment profiles**: private defaults; no public unrestricted agent exposure

***REMOVED******REMOVED******REMOVED*** Guardrails (explicit)

This H-layer **does not**:

- build one-click public autonomous agents
- expose runtime agents publicly
- implement uncontrolled deployment automation
- mutate static prompt prefixes during sessions
- change tool schemas mid-session (detection only)
- switch models mid-session without explicit reset metadata
- insert timestamps/random IDs into static prompt prefixes
- introduce hidden cache optimization logic
- bypass H-039 firewall or H-049 identity governance

***REMOVED******REMOVED******REMOVED*** Prompt caching discipline

***REMOVED******REMOVED******REMOVED******REMOVED*** Static prefix
The static prefix is a deterministic set of components (examples):

- `system_rules`
- `tool_definitions`
- `schema_definitions`
- `project_context`
- `guardrails`
- `behavior_guidelines`

Static prefix components are hashed deterministically and validated to reject volatile content.

***REMOVED******REMOVED******REMOVED******REMOVED*** Dynamic suffix
The dynamic suffix contains runtime growth components:

- `user_messages`
- `assistant_turns`
- `tool_outputs`
- `runtime_observations`
- `event_stream_updates`
- `approval_events`

The suffix **must not** mutate the static prefix. All suffix metadata is auditable.

***REMOVED******REMOVED******REMOVED******REMOVED*** Cache breakpoints
Cache boundaries are represented explicitly with:

- `static_prefix_hash`
- `dynamic_suffix_start_index`
- `cache_valid` with an **explainable** `invalidation_reason`

Invalidation reasons are never hidden.

***REMOVED******REMOVED******REMOVED******REMOVED*** Cache efficiency formula

\[
\text{cache_efficiency_ratio}=\frac{\text{cache_read_input_tokens}}{\text{cache_read_input_tokens}+\text{cache_creation_input_tokens}}
\]

The foundation implementation uses deterministic heuristics for savings estimates and does **not** claim provider-specific costs.

***REMOVED******REMOVED******REMOVED*** Typed context integration (H-044)

H-050 adds cache-aware context support **without introducing new H-044 `context_type` values**.

- `static_prefix_context` is represented as `knowledge_context` with tags:
  - `cacheable_context`, `static_prefix_context`
- `dynamic_suffix_context` is represented as `memory_context` with tags:
  - `dynamic_suffix_context`, `volatile_context`

This keeps the H-044 type system stable while still allowing cache governance projections.

***REMOVED******REMOVED******REMOVED*** Deployment profiles (governed)

Deployment profiles are metadata-only and include:

- runtime visibility (foundation rejects public)
- allowed channels (external channels require identity + firewall + approval)
- private runtime requirement
- approval requirement

***REMOVED******REMOVED******REMOVED*** Routers (thin)

- Cache governance:
  - `/api/v1/system/cache/static-prefix`
  - `/api/v1/system/cache/dynamic-suffix`
  - `/api/v1/system/cache/breakpoints`
  - `/api/v1/system/cache/efficiency`
  - `/api/v1/system/cache/tool-schema-stability`
  - `/api/v1/system/cache/model-session-stability`
  - `/api/v1/system/cache/compression`
- Deployment governance:
  - `/api/v1/system/deployment/profiles`
  - `/api/v1/system/deployment/channels`
  - `/api/v1/system/deployment/private-runtime`
  - `/api/v1/system/deployment/safety`

***REMOVED******REMOVED******REMOVED*** Operational integrations

- **H-041 inference runtime telemetry** surfaces cache efficiency, prefill savings estimate, and breakpoint validity.
- **H-048 event streams** include cache-related metadata events (created/read/invalidated/compression started, warnings).
- **H-039 firewall** recognizes H-050 policy domains for detection/governance.

