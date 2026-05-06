***REMOVED*** H-034 — Semantic Capability Graph & AI-Native Backend Abstraction Layer

**Scope:** Foundation — static semantic entities, edges, contracts, topology summaries. **No** ontology megamodels or distributed semantic meshes.

***REMOVED******REMOVED*** H-020 coordination

- **`GET /api/v1/system/capabilities`** remains the **flat capability manifest** (H-020).
- Each catalog export now includes **`semantic_capability_graph`**: schema version, topology summary, and links to graph routes.

***REMOVED******REMOVED*** Graph routes (same host; sub-paths)

| GET | Purpose |
|-----|---------|
| `/api/v1/system/capabilities/graph` | Semantic entity registry |
| `/api/v1/system/capabilities/topology` | Full graph + summary + dependency/trust paths |
| `/api/v1/system/capabilities/contracts` | Interaction contracts |
| `/api/v1/system/capabilities/awareness` | Cross-capability awareness summaries |
| `/api/v1/system/capabilities/runtime-context` | Curated runtime semantic snapshot |

Envelope: `semantic_capability_graph_foundation`, `recursive_capability_mutation=false`, `autonomous_capability_discovery=false`, `distributed_semantic_mesh=false`.

***REMOVED******REMOVED*** Concepts

- **Entities**: `runtime_context`, `workflow_governance`, `trajectory_evaluation`, `graph_intelligence`, `reliability_governance`, `agent_security`.
- **Edges**: `depends_on`, `trusted_by`, `evaluated_by`, `orchestrated_by`, `secured_by`, `enriched_by` (subset used in static graph).
- **Contracts**: Source/target capability pairs with allowed actions, trust requirements, escalation, visibility.

***REMOVED******REMOVED*** Explicit deferrals

- Giant ontology systems and recursive semantic mutation.
- Autonomous capability discovery and uncontrolled orchestration expansion.
- Distributed telemetry / semantic meshes replacing FastAPI routes.

***REMOVED******REMOVED*** Verification

```bash
python scripts/verify_h034_semantic_capability_graph.py
cd backend && python -m pytest tests/test_semantic_capability_graph.py -q
```
