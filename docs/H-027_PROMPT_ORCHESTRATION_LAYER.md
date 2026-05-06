***REMOVED*** H-027 — Structured Prompt Orchestration & Evaluation Layer

**Classification:** Foundation-Level Incremental  
**Status:** Foundation implemented (deterministic registries and scoring — no LLM execution in this layer)

***REMOVED******REMOVED*** Prompt strategy selection

Approved strategies (`direct_prompting`, `json_prompting`, `role_prompting`, `negative_prompting`, `arq_reasoning`, `few_shot_prompting`, `constrained_summary`) are **statically registered** with hierarchy ranks. Runtime cannot invent new strategy IDs.

***REMOVED******REMOVED*** ARQ reasoning

**ARQ** here means **explicit checklist templates** (`arq_template_service`) — procurement analysis, opportunity evaluation, graph confidence, market signal validation. Steps are visible strings, not hidden scratchpads.

***REMOVED******REMOVED*** JSON contracts

`json_contract_service` pins named contracts (`results_hub_v1`, `widget_render_v1`, `graph_insight_v1`, `opportunity_rank_v1`) so downstream agents emit **bounded shapes**, not arbitrary JSON.

***REMOVED******REMOVED*** Role prompting

Five approved personas with fixed commercial templates — **no arbitrary persona injection**.

***REMOVED******REMOVED*** Negative prompting

Evaluation rewards `include_negative_constraints` so refusal boundaries and exclusion lists are **first-class**, not bolted on silently.

***REMOVED******REMOVED*** Prompt hierarchy

Strategy metadata includes `hierarchy_rank` for governance comparisons when overrides diverge from policy defaults.

***REMOVED******REMOVED*** Deterministic orchestration

`reasoning_policy_service` maps task types (e.g. `graph_reasoning` → `arq_reasoning`) with printed rationales. `prompt_evaluation_service` scores configurations **without calling remote models**.

***REMOVED******REMOVED*** Explicitly deferred

- Autonomous prompt evolution / self-modifying prompt stores  
- Unrestricted chain-of-thought exposure to clients  
- Self-hosted DeepSeek-class infra migrations  
- Recursive multi-agent planners  

***REMOVED******REMOVED*** Related artefacts

- Proof: `docs/H-027_IMPLEMENTATION_PROOF.md`  
- Verification: `scripts/verify_h027_prompt_orchestration.py`  
- API: `/api/v1/system/prompts/*`
