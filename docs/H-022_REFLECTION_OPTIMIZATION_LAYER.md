***REMOVED*** H-022 — Reflection-Driven Prompt Optimization Layer

**Status**: Foundation Implemented — autonomous optimization / RL / production auto-deploy explicitly deferred.

***REMOVED******REMOVED*** GEPA-style reflection (product framing)

GEPA-inspired workflows emphasize **trace → diagnose → propose → review → (optional) adopt** under human governance. This repository implements **structured traces**, **deterministic revision templates**, and **human-gated candidates**—not learned policy updates.

***REMOVED******REMOVED*** Why SOAR B2B benefits

- **Results Hub** and **Opportunity Engine** outputs compound errors unless orchestration and prompts improve deliberately.
- **Intelligence Graph** reasoning needs structured diagnostics (low-confidence edges, repeated clusters).
- **Generative UI** (H-019) benefits from reviewable prompt deltas, not silent template drift.

***REMOVED******REMOVED*** Prompt optimization vs reinforcement learning vs fine-tuning

| Approach | This layer |
|----------|------------|
| Prompt optimization (governed) | Structured traces + template recommendations + human approval |
| Reinforcement learning | **Not implemented** — no online reward loops |
| Model fine-tuning | **Not implemented** — no weight updates |

***REMOVED******REMOVED*** Why this avoids autonomous self-modification

- Candidates stay **`pending`** until explicit **`approve`** / **`reject`** actions with reviewer identity.
- **No production prompt mutation** occurs inside these endpoints; downstream deployment remains a separate controlled process.
- API envelopes always carry **`autonomous_execution: false`**.

***REMOVED******REMOVED*** Approved first use cases

- Results Hub narrative refinement
- Opportunity ranking prompt scaffolding
- Graph reasoning diagnostics
- Generative UI instruction review

***REMOVED******REMOVED*** Explicitly deferred

- Autonomous prompt evolution and recursive self-improvement loops
- Production auto-deployment from this API surface
- External LLM calls for “creative” rewrite inside the foundation layer

***REMOVED******REMOVED*** Verification

Run `python scripts/verify_h022_reflection_layer.py` and `pytest backend/tests/test_reflection_optimization.py`.
