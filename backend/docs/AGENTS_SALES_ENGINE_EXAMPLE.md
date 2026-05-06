***REMOVED*** Autonomous Sales Agent — Example Request & Output

***REMOVED******REMOVED*** POST /agents/sales-engine/run

***REMOVED******REMOVED******REMOVED*** Example request

```json
{
  "industry": "fiber infrastructure",
  "location": "Texas",
  "target_roles": [
    "CEO",
    "CTO",
    "Procurement Director",
    "VP Operations"
  ],
  "campaign_goal": "introduce fiber subcontracting services"
}
```

***REMOVED******REMOVED******REMOVED*** Example with optional fields

```json
{
  "industry": "fiber infrastructure",
  "location": "Texas",
  "target_roles": ["CEO", "CTO", "Procurement Director", "VP Operations"],
  "campaign_goal": "introduce fiber subcontracting services",
  "keywords": ["broadband", "FTTH"],
  "company_size": "11-50"
}
```

***REMOVED******REMOVED******REMOVED*** Example output

```json
{
  "companies_found": 42,
  "leads_generated": 115,
  "emails_generated": 115,
  "agent_run_id": "run_89273a1b4c5d",
  "status": "completed"
}
```

***REMOVED******REMOVED******REMOVED*** cURL

```bash
curl -X POST "http://localhost:8000/agents/sales-engine/run" \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "fiber infrastructure",
    "location": "Texas",
    "target_roles": ["CEO", "CTO", "Procurement Director", "VP Operations"],
    "campaign_goal": "introduce fiber subcontracting services"
  }'
```

---

***REMOVED******REMOVED*** GET /agents/runs

List recent agent runs (from PostgreSQL).

**Query:** `?limit=50&workflow_type=sales_engine`

**Response:** Array of `{ agent_run_id, workflow_type, status, created_at }`.

---

***REMOVED******REMOVED*** GET /agents/runs/{id}

Get one run and its step logs (workflow_step, token_usage, latency_ms, error_message).

---

***REMOVED******REMOVED*** POST /agents/classify-response

Classify a reply email and get suggested follow-up.

***REMOVED******REMOVED******REMOVED*** Request

```json
{
  "reply_email_body": "Thanks for reaching out. We might be interested in Q2. Can you send more details on pricing?"
}
```

***REMOVED******REMOVED******REMOVED*** Response

```json
{
  "classification": "neutral",
  "reasoning": "Sender shows conditional interest and asks for more information.",
  "followup_subject": "Re: More details on pricing",
  "followup_body": "Thank you for your reply. Here are the key pricing options...",
  "suggested_action": "Send when appropriate"
}
```

Classifications: `positive_interest` | `neutral` | `not_now` | `not_interested`.

---

***REMOVED******REMOVED*** Workflow steps (logged to PostgreSQL)

1. company_discovery — industry, location, keywords, company size
2. company_analysis — LLM: what company does, pain points, outreach relevance
3. persona_detection — LLM: decision makers (CEO, CTO, etc.)
4. contact_enrichment — email, LinkedIn, website (graceful fail)
5. email_generation — OpenAI: subject + body per contact
6. outreach_queue — push to Redis queue (optional), summary

Response flow: **response_classification** → **followup_generation** (via POST /agents/classify-response).
