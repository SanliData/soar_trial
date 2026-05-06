***REMOVED*** Autonomous Lead Generation Agent — Example Request

***REMOVED******REMOVED*** Endpoint

```
POST /agents/lead-generation
```

***REMOVED******REMOVED*** Example request body

```json
{
  "industry": "fiber infrastructure",
  "location": "Texas",
  "decision_roles": ["CTO", "Procurement", "Director"]
}
```

***REMOVED******REMOVED*** Example with keywords

```json
{
  "industry": "fiber infrastructure",
  "location": "Texas",
  "decision_roles": ["CTO", "Procurement", "Director"],
  "keywords": ["broadband", "FTTH"]
}
```

***REMOVED******REMOVED*** cURL

```bash
curl -X POST "http://localhost:8000/agents/lead-generation" \
  -H "Content-Type: application/json" \
  -d '{"industry":"fiber infrastructure","location":"Texas","decision_roles":["CTO","Procurement","Director"]}'
```

***REMOVED******REMOVED*** Expected response shape

```json
{
  "companies": [
    {
      "company": "Example Fiber LLC",
      "website": "https://example-fiber.com",
      "contacts": [
        {
          "name": "Jane Doe",
          "role": "CTO",
          "email": "contact@example-fiber.com",
          "linkedin": "https://linkedin.com/in/placeholder-cto",
          "generated_email": "Hi Jane, ..."
        }
      ]
    }
  ],
  "job_id": "uuid-optional",
  "status": "completed",
  "error": null
}
```

***REMOVED******REMOVED*** Poll job result (when using Redis)

```
GET /agents/lead-generation/jobs/{job_id}
```

***REMOVED******REMOVED*** Health

```
GET /agents/health
```

***REMOVED******REMOVED*** Requirements

- `OPENAI_API_KEY` env set for persona extraction and email generation (optional; skills fall back gracefully if missing).
- Redis optional; used for job storage when available.
