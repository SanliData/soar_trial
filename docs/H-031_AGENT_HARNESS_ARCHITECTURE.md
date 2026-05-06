***REMOVED*** H-031 — Agent Harness Architecture & Modular Cognitive Runtime Layer

**Scope:** Foundation — static registries, deterministic compression, explicit sub-agent caps. **No** recursive swarms or distributed orchestration.

***REMOVED******REMOVED*** Architecture

The harness separates concerns into **memory domains**, **skills**, **protocols**, and **evaluation routing**, coordinated through a small **runtime summary** surface and **compression** helpers with visible truncation markers.

***REMOVED******REMOVED*** Memory domains

Types: `working_memory`, `semantic_memory`, `episodic_memory`, `user_context_memory`, `workflow_memory`. Each has lifecycle and mutation policy metadata — **no unrestricted mutation API** in this foundation.

***REMOVED******REMOVED*** Skills

Fixed catalog (`procurement_analysis`, `opportunity_evaluation`, `graph_investigation`, `onboarding_planning`, `executive_summarization`, `market_signal_review`) with category and risk tier — **no runtime skill registration**.

***REMOVED******REMOVED*** Protocols

`agent_to_user`, `agent_to_tool`, `agent_to_agent`, `evaluation_protocol`, `escalation_protocol` — envelope and trust metadata; delegation requires explicit manifests.

***REMOVED******REMOVED*** Evaluation routing

Workflow labels map deterministically to evaluation destinations (`graph` → `graph_evaluation`, etc.) via static lookup.

***REMOVED******REMOVED*** Compression

Modes: `context`, `trajectory`, `memory`. Uses **`[HARNESS_CONTEXT_TRUNCATED]`** markers when shortening text; trajectory compression caps step count with digest metadata.

***REMOVED******REMOVED*** Sub-agent boundaries

Foundation cap **4** sub-agents per session; scopes allow-listed; permissions must use approved prefixes (`read:`, `execute:`, `delegate:`).

***REMOVED******REMOVED*** HTTP surface

| Method | Path |
|--------|------|
| GET | `/api/v1/system/harness/memory` |
| GET | `/api/v1/system/harness/skills` |
| GET | `/api/v1/system/harness/protocols` |
| POST | `/api/v1/system/harness/compress` |
| GET | `/api/v1/system/harness/runtime-summary` |

Envelope: `agent_harness_foundation`, `recursive_agent_swarm=false`, `unrestricted_subagent_spawning=false`.

***REMOVED******REMOVED*** Semantic capabilities

`harness.memory`, `harness.skills`, `harness.protocols`, `harness.compress`, `harness.runtime_summary` — **orchestration_safe=true**, **destructive_action=false**.

***REMOVED******REMOVED*** Explicit deferrals

- Recursive autonomous swarms and CrewAI-scale meshes.
- Unrestricted memory mutation and hidden delegation.
- Distributed orchestration infrastructure.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h031_agent_harness.py
cd backend && python -m pytest tests/test_agent_harness.py -q
```
