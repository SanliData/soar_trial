***REMOVED*** Agent pipeline flow

End-to-end flow from user request to LLM response:

```
User Request
    ↓
Context Engine
    ↓
Agent Reasoning
    ↓
Skill Execution
    ↓
Tool Results
    ↓
Updated Context
    ↓
LLM Response
```

***REMOVED******REMOVED*** 1. User Request

Incoming payload (e.g. from `/agents/lead-generation` or chat):

- `industry`, `location`, `keywords`, `decision_roles` → lead generation
- `question` → analytics/NL query
- Optional: `intent`, `session_id`, `history`

***REMOVED******REMOVED*** 2. Context Engine

**Module:** `src.agents.context_engine.build_context_from_request()`

- Normalizes the user request into a **context** dict.
- Infers **intent** (e.g. `lead_generation`, `analytics_query`).
- Extracts **entities** (industry, location, roles, question, etc.).
- Optionally attaches **available_skills** and **history** for the agent.

Output: `context` passed to Agent Reasoning.

***REMOVED******REMOVED*** 3. Agent Reasoning

**Module:** `src.agents.agent_pipeline` (inside `run_agent_pipeline()`)

- Uses **intent** and **entities** to choose the **skill sequence**.
- Example: `lead_generation` → `company_discovery` → `company_analysis` → `company_filter` → `decision_maker_detection` → `contact_enrichment` → `email_generation`.

Can be overridden by passing `skill_sequence` into the pipeline.

***REMOVED******REMOVED*** 4. Skill Execution

**Module:** `src.skills.skill_executor.run_pipeline()` (async) or `src.sales_skills.skill_executor.run_skill_sequence()` (sync)

- Runs each skill in order with the current context.
- Each skill’s return value is merged into the context for the next step.

***REMOVED******REMOVED*** 5. Tool Results

- Each skill acts as a “tool”; its return dict (e.g. `companies`, `contacts`, `token_usage`) is the tool result.
- These are merged into the shared context (see Updated Context).

***REMOVED******REMOVED*** 6. Updated Context

- Context after all skills have run: contains `companies`, `contacts`, `run_id`, `errors` (if any), etc.
- This is the **final context** used to form the LLM response.

***REMOVED******REMOVED*** 7. LLM Response

**Module:** `src.agents.agent_pipeline._build_llm_response()`

- Builds a short natural-language summary from the updated context (e.g. “Found N companies and M contacts”).
- Can be replaced or extended with a real LLM call (OpenAI) for a richer reply.

---

***REMOVED******REMOVED*** Usage

**Pipeline (full flow):**

```python
from src.agents.agent_pipeline import run_agent_pipeline

context = await run_agent_pipeline(
    {"industry": "Technology", "location": "Texas", "decision_roles": ["CTO"]},
    session_id="sess_123",
    include_llm_response=True,
)
***REMOVED*** context["llm_response"], context["companies"], context["run_id"], etc.
```

**Context only (no skills):**

```python
from src.agents.context_engine import build_context_from_request

context = build_context_from_request({"industry": "Healthcare", "location": "California"})
***REMOVED*** context["intent"], context["entities"], context["available_skills"]
```
