***REMOVED*** H-032 — Delegated Autonomous Workflow Execution & Adaptive Effort Governance Layer

**Scope:** Foundation — static contracts, deterministic effort and decay heuristics, in-memory session tracking, explicit delegation and parallel caps. **No** unrestricted autonomous execution or distributed orchestration.

***REMOVED******REMOVED*** Delegated workflow execution

Named workflows (e.g. `procurement_analysis`, `graph_investigation`) ship as **versioned, immutable contracts**: objective, constraints, acceptance criteria, recommended effort, `allowed_tools`, escalation policy, and `output_contract`. There is **no API to add or edit contracts at runtime**.

***REMOVED******REMOVED*** Adaptive effort governance

Effort bands: `low`, `medium`, `high`, `xhigh`, `max`. Assignment is a **static lookup** by workflow name or task kind, with an explainable `routing_rule` field on each resolution.

***REMOVED******REMOVED*** Workflow contracts

See `workflow_contract_registry.py` — exports include `contracts`, `contract_count`, `mutation_policy=static_registry_only`.

***REMOVED******REMOVED*** Session lifecycle

Sessions are created for known workflow names only. Operations: **create**, **summarize** (deterministic snapshot from stored counters), **checkpoint**, **close**. Foundation storage is **in-process** (development footprint).

***REMOVED******REMOVED*** Context decay handling

`detect_context_rot` blends token and turn pressure into a **rot_score**. Recommendations cover compression tier, optional session reset, and **head-keep summarization** with `[WORKFLOW_CONTEXT_TRUNCATED]` when trimming.

***REMOVED******REMOVED*** Controlled parallelization

Policies `bounded_fanout` and `sequential_only`; hard cap **`MAX_PARALLEL_SUBTASKS`**. Explicit `policy_id` required — no implicit parallelism.

***REMOVED******REMOVED*** Acceptance validation

Completion checks ensure **acceptance criteria keys** appear in the outputs object, plus **`constraints_respected`** and **`escalation_acknowledged`** flags.

***REMOVED******REMOVED*** HTTP surface

| Method | Path |
|--------|------|
| GET | `/api/v1/system/workflows/contracts` |
| GET | `/api/v1/system/workflows/effort-levels` |
| POST | `/api/v1/system/workflows/session` |
| POST | `/api/v1/system/workflows/compress` |
| POST | `/api/v1/system/workflows/validate` |
| GET | `/api/v1/system/workflows/runtime-summary` |

Envelope: `workflow_governance_foundation`, `unrestricted_autonomous_execution=false`, `recursive_workflow_swarm=false`.

***REMOVED******REMOVED*** Semantic capabilities

`workflows.contracts`, `workflows.sessions`, `workflows.compress`, `workflows.validate`, `workflows.runtime_summary` — **orchestration_safe=true**, **destructive_action=false**.

***REMOVED******REMOVED*** Explicit deferrals

- Unrestricted autonomous swarms and recursive orchestration meshes.
- Self-expanding workflow graphs and uncontrolled parallel execution.
- Distributed orchestration infrastructure.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h032_workflow_governance.py
cd backend && python -m pytest tests/test_workflow_governance.py -q
```
