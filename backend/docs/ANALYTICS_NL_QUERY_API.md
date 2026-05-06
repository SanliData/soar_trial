***REMOVED*** Sales Data Analytics API (Natural Language Query)

SOARB2B exposes a natural language query endpoint that uses the **Company Intelligence Graph** to plan and validate SQL. User input is never concatenated into SQL; only structured intent (tables, group_by, metric, time_range) drives query generation.

***REMOVED******REMOVED*** Endpoint

- **POST** `/v1/analytics/query`

***REMOVED******REMOVED*** Request

```json
{
  "question": "Which industries generated the most replies last quarter?"
}
```

- `question` (required): Natural language question, 1–2000 characters.

***REMOVED******REMOVED*** Response

```json
{
  "sql_used": "SELECT \"industry_performance\".industry AS group_key, COUNT(*) AS cnt FROM \"industry_performance\" GROUP BY \"industry_performance\".industry ORDER BY cnt DESC LIMIT :limit",
  "result": [
    { "group_key": "Technology", "cnt": 42 },
    { "group_key": "Healthcare", "cnt": 31 }
  ],
  "summary": "Returned 2 row(s)."
}
```

- `sql_used`: The parameterized SQL that was executed (for transparency and debugging).
- `result`: Array of row objects (key-value).
- `summary`: Short text summary of the result.

***REMOVED******REMOVED*** Example questions

- "Which industries respond best to our outreach campaigns?"
- "Which companies in Texas have CTO contacts?"
- "Which campaigns generated the highest reply rate?"
- "Which industries generated the most replies last quarter?"

***REMOVED******REMOVED*** Pipeline

1. **question_parser** – Maps question to structured intent (tables, group_by, metric, time_range).
2. **graph_sql_planner** – Uses the schema graph to pick tables and join path.
3. **sql_generator** – Builds parameterized SQL from the plan only.
4. **query_validator** – Ensures SELECT-only and whitelisted tables/columns.
5. Database execution (with timeout, default 30s).
6. **response_formatter** – Returns `result` and `summary`.

***REMOVED******REMOVED*** Monitoring

Failures are classified for the monitoring agent:

- `analytics_query_failure` – SQL execution or pipeline error.
- `graph_generation_failure` – Schema graph build failed.
- `invalid_sql_generation` – Generated SQL rejected by validator.
- `query_timeout` – Query exceeded timeout.
- `nl_query_parsing_error` – Intent parsing failed.

Alerts include: incident title, severity, affected module, likely source files, suggested next step.

***REMOVED******REMOVED*** Security

- Only **SELECT** queries are allowed.
- Tables and columns are **whitelisted** from the schema graph.
- User-supplied text is **never** concatenated into SQL; only structured intent drives generation.
- Query timeout (e.g. 30s) limits resource use.
