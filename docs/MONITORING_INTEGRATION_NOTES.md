***REMOVED*** SOARB2B Monitoring Agent – Integration Notes

This document describes how the AI DevOps Monitoring Agent is wired to the real SOARB2B codebase: log sources, incident types, modules, and routes.

---

***REMOVED******REMOVED*** 1. Log sources

| Source | Location / mechanism | Used for |
|--------|----------------------|----------|
| **PM2 error log** | `backend/logs/soarb2b-error.log` (ecosystem.config.cjs: `error_file`) | Uvicorn/Python errors, unhandled exceptions |
| **PM2 out log** | `backend/logs/soarb2b-out.log` (`out_file`) | Stdout; errors may appear here if not separated |
| **Application logs** | Python `logging` to stderr (no file handler in app.py) | Captured by PM2 into the above files |
| **Agent run logs (DB)** | `agent_run_logs` table (`error_message` not null) | Workflow/skill step failures (e.g. `workflow_step`, `agent_run_id`) |

The global exception handler in `src/app.py` logs with `logger.error("Unhandled error", exc_info=True)`. Request IDs come from `RequestIDMiddleware` (`request.state.request_id`, `X-Request-ID` header).

---

***REMOVED******REMOVED*** 2. Real module → incident type mapping

| Incident type | Real modules / touchpoints |
|---------------|----------------------------|
| `lead_generation_workflow_failure` | `src/workflows/lead_generation_workflow.py`, `src/agents/workflows/lead_generation_workflow.py` |
| `company_discovery_failure` | `src/skills/discovery/company_discovery_skill.py`, `src/agents/skills/company_discovery.py` |
| `decision_maker_detection_failure` | `src/skills/persona/decision_maker_detection_skill.py`, `src/agents/skills/persona_detection.py` |
| `contact_enrichment_failure` | `src/skills/enrichment/contact_enrichment_skill.py`, `src/agents/skills/contact_enrichment.py` |
| `email_generation_failure` | `src/skills/outreach/email_generation_skill.py`, `src/agents/skills/email_generation.py` |
| `campaign_creation_failure` | `src/agents/skills/campaign_creation.py` |
| `campaign_dispatch_failure` | `src/automation/outreach_queue.py`, `src/automation/campaign_engine.py`, `src/agents/skills/outreach_queue.py` |
| `response_classification_failure` | `src/automation/response_classifier.py`, `src/agents/skills/response_classification.py` |
| `learning_engine_failure` | `src/learning/learning_engine.py` |
| `redis_queue_failure` | `src/core/cache.py` (`get_redis_client`), `src/middleware/rate_limit_redis.py` |
| `openai_timeout` / `openai_invalid_response` / `openai_rate_limit` | All skills and agents that call `openai.OpenAI(...)` (see grep for `OpenAI(`) |
| `malformed_workflow_context` | `src/skills/skill_executor.py`, workflow context between skills |
| `db_write_failure` | `src/db/base.py` (SessionLocal), any model commit |
| `authentication_flow_failure` / `oauth_callback_failure` / `jwt_validation_failure` | Auth routes, Google OAuth, JWT validation |
| `rate_limit_issue` | `src/middleware/rate_limiting_middleware.py` |
| `malformed_payload_issue` | FastAPI `RequestValidationError` (422) |
| `external_api_integration_issue` | Any `requests.*` or external HTTP client usage |

---

***REMOVED******REMOVED*** 3. Likely source files (GitHub context finder)

The monitor infers likely files from:

- **Module names** in log lines and from `agent_run_logs.workflow_step`
- **Affected components** (skill/workflow/endpoint names)
- **Known map** in `src/monitoring/github_context_finder.py`: `MODULE_TO_PATH` (skills, workflows, agents, automation, learning, run_logger, app)
- **Route context** from `ENDPOINT_TO_ROUTE` (e.g. `/agents/lead-generation` → agents_router)

No GitHub API is used; paths are derived from the repo layout under `backend/src/`.

---

***REMOVED******REMOVED*** 4. API routes (monitoring and style)

Monitoring endpoints follow the same pattern as other v1 routers (e.g. `agents_router`, `sales_engine_router`):

- **Prefix:** ` /monitoring`
- **Router file:** `src/http/v1/monitoring_router.py`
- **Registration:** Included in `src/app.py` with `app.include_router(monitoring_router)`

| Endpoint | Purpose |
|----------|---------|
| `GET /monitoring/incidents` | List incidents (optional `?status=`, `?limit=`) |
| `GET /monitoring/incidents/{incident_id}` | Single incident + events |
| `POST /monitoring/run` | Run the monitoring agent once |
| `GET /monitoring/runs` | List recent monitoring runs |

There is no admin-only guard on these routes; add one (e.g. `X-Admin-Key` or JWT) if you want to restrict access.

---

***REMOVED******REMOVED*** 5. Database and session usage

- **Session pattern:** `SessionLocal()` from `src.db.base`; session is closed in `finally` (same as `src/agents/run_logger.py` and other services).
- **Models:** `Incident`, `IncidentEvent`, `MonitoringRun` in `src/monitoring/models/`; they use `src.db.base.Base` and are imported in `src/models/__init__.py` so `create_all` creates the tables.
- **New columns (optional):** `Incident.affected_endpoint`, `Incident.affected_workflow`, `Incident.request_ids`. If you use migrations, add a migration for these; otherwise ensure `init_db()` or equivalent is run after the change.

---

***REMOVED******REMOVED*** 6. Scheduling and background work

- **Scheduler:** `src/monitoring/scheduler.py` starts a background asyncio task when `MONITORING_AGENT_ENABLED=true` (e.g. in env). It runs the agent every 5 minutes.
- **Startup:** The scheduler is started in `app.py`’s `startup_config_and_redis` (after the Redis check in production). It does not block request threads.
- **Manual run:** `POST /monitoring/run` runs the agent synchronously in the request (no Redis queue). For very large runs, consider moving to a Redis-backed job and returning a job id.

---

***REMOVED******REMOVED*** 7. OpenAI usage in monitoring

- **Where:** Root cause summarization and suggested next step in `src/monitoring/root_cause_analyzer.py` (optional, when `use_openai=True`).
- **Client:** Uses `openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))` like the rest of the app (no separate wrapper). No new central OpenAI layer was introduced.

---

***REMOVED******REMOVED*** 8. Example real incident payloads

**Workflow step failure (from agent_run_logs):**

- `workflow_step`: `email_generation`
- `error_message`: `OpenAI API timeout`
- **Normalized type:** `openai_timeout`
- **Likely files:** `backend/src/skills/outreach/email_generation_skill.py`, `backend/src/agents/skills/email_generation.py`

**PM2 log line (parsed):**

- Raw: `ERROR ... openai.RateLimitError: Rate limit exceeded ...`
- **Parsed:** `exception_type`: `openai.RateLimitError`, `error_type`: `openai_rate_limit`
- **Affected area:** From module in traceback or from workflow_step if present

**Alert format (concise, ops-friendly):**

- Severity, Incident Title, Affected Area (route / workflow), Occurrences, Time Window
- Impacted Components, Likely Root Cause, Suggested Immediate Action
- Likely Source Files, Status (new / recurring / escalated)

---

***REMOVED******REMOVED*** 9. Minimal logging changes

No app-wide logging stack was replaced. The monitor reads:

- Existing stderr/PM2 logs
- Existing `agent_run_logs` rows with `error_message` set

To improve monitoring quality you can:

- Ensure `logger.error(..., exc_info=True)` is used in critical paths (already done in the global exception handler).
- Optionally log `request_id` (e.g. from `request.state.request_id`) in a few key routes or in middleware so it appears in log lines and can be parsed by the ingestor.
