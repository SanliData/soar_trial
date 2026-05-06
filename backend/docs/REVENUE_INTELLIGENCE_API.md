***REMOVED*** Revenue Intelligence System – API Examples

***REMOVED******REMOVED*** Company Graph

**GET /v1/graph/company/{id}**

Response:
```json
{
  "company": {"id": "company_123", "type": "company", "label": "AT&T", "properties": {"industry": "Telecommunications", "location": "Texas"}},
  "contacts": [{"id": "contact_456", "type": "contact", "label": "Jane Doe", "properties": {"role": "CTO"}}]
}
```

**GET /v1/graph/similar/{id}?limit=10**

Response:
```json
{
  "company": "AT&T",
  "similar_companies": [
    {"name": "Lumen", "score": 0.86},
    {"name": "Frontier Communications", "score": 0.82}
  ]
}
```

**POST /v1/graph/refresh** – Build and cache graph (background/admin).

---

***REMOVED******REMOVED*** Market Signals

**GET /v1/signals/industry?industry=fiber+infrastructure**

**GET /v1/signals/region?region=Texas**

Response:
```json
{
  "signals": [{"type": "industry_engagement_surge", "industry": "fiber infrastructure", "region": "Texas", "confidence": 0.78}],
  "stored": []
}
```

---

***REMOVED******REMOVED*** Opportunities

**GET /v1/opportunities/recommendations?industry=fiber+infrastructure&region=Texas**

Response:
```json
{
  "industry": "fiber infrastructure",
  "region": "Texas",
  "recommended_companies": [
    {
      "company": "FiberWave Networks",
      "target_persona": "VP Operations",
      "reason": "Similar companies responded to campaigns + industry signal"
    }
  ]
}
```

---

***REMOVED******REMOVED*** Context layers (agent)

Use `build_layered_context()` for agents; layers (in order): instructions, examples, knowledge, memory, tools, tool_results, market_intelligence.

***REMOVED******REMOVED*** LLM Router

- `get_model_for_task("classification")` → gpt-3.5-turbo  
- `get_model_for_task("email_generation")` → gpt-4  
- `route_and_call(task_type, messages)` → calls OpenAI with the selected model.
