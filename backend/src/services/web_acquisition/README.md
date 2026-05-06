***REMOVED*** Web Acquisition Service (Stagehand Optional)

***REMOVED******REMOVED*** Overview

The Web Acquisition service provides optional web scraping/enrichment capabilities using Browserbase Stagehand. It is feature-flagged and provides a dry-run mode when disabled.

***REMOVED******REMOVED*** Features

- **Async Job Model**: Acquisition jobs run asynchronously, never inline in API requests
- **Cap Enforcement**: Respects MAX 100 results limit (or admin override)
- **Compliance Guardrails**: Sources policy, blocklist, rate limiting
- **Export Formats**: CSV and JSON export endpoints
- **Results Hub Integration**: Results appear in Results Hub UI

***REMOVED******REMOVED*** Configuration

***REMOVED******REMOVED******REMOVED*** Environment Variables

```bash
***REMOVED*** Enable Stagehand integration (default: false)
SOAR_ENABLE_STAGEHAND=true

***REMOVED*** Browserbase API credentials (required if Stagehand enabled)
BROWSERBASE_API_KEY=your_api_key_here
BROWSERBASE_API_URL=https://www.browserbase.com/v1
```

***REMOVED******REMOVED******REMOVED*** Feature Flag

When `SOAR_ENABLE_STAGEHAND=false` (default), the service runs in **dry-run mode** and returns mocked results for testing.

***REMOVED******REMOVED*** API Endpoints

***REMOVED******REMOVED******REMOVED*** POST `/api/v1/b2b/acquisition/jobs`

Create a new acquisition job.

**Request:**
```json
{
  "plan_id": "plan_abc123",
  "target_type": "both",
  "geography": {
    "region": "Istanbul",
    "country": "Turkey"
  },
  "sources_policy": "official_only",
  "max_results": 100
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "uuid-here",
  "status": "queued",
  "message": "Acquisition job created..."
}
```

***REMOVED******REMOVED******REMOVED*** GET `/api/v1/b2b/acquisition/jobs?plan_id={plan_id}`

List acquisition jobs (optionally filtered by plan_id and status).

***REMOVED******REMOVED******REMOVED*** GET `/api/v1/b2b/acquisition/jobs/{job_id}`

Get job status and coverage report.

**Response:**
```json
{
  "job_id": "uuid-here",
  "plan_id": "plan_abc123",
  "status": "ready",
  "coverage_report": {
    "businesses_found": 45,
    "contacts_found": 23,
    "emails": 18,
    "phones": 31,
    "websites": 45,
    "is_capped": false
  }
}
```

***REMOVED******REMOVED******REMOVED*** GET `/api/v1/b2b/acquisition/jobs/{job_id}/export.csv`

Download results as CSV.

***REMOVED******REMOVED******REMOVED*** GET `/api/v1/b2b/acquisition/jobs/{job_id}/export.json`

Download results as JSON.

***REMOVED******REMOVED*** Sources Policy

***REMOVED******REMOVED******REMOVED*** `official_only` (default)

Only allows:
- Government domains (gov.tr, gov.uk, etc.)
- Municipality domains
- Chamber of commerce domains
- Company websites (not restricted platforms)

***REMOVED******REMOVED******REMOVED*** `public_web`

Adds:
- Generic web directories (Google, Bing, Yellow Pages, etc.)

**Restricted Domains (always blocked):**
- LinkedIn
- Facebook
- Twitter/X
- Instagram
- WhatsApp
- Other social media platforms

***REMOVED******REMOVED*** Job Statuses

- `queued`: Job created, waiting to start
- `running`: Job is executing
- `ready`: Job completed successfully, results available
- `failed`: Job failed (check error_message)

***REMOVED******REMOVED*** Worker Execution

***REMOVED******REMOVED******REMOVED*** Option A: Cloud Run Job (Production - Preferred)

Trigger a Cloud Run Job from an admin-only endpoint:

```bash
***REMOVED*** Admin-only endpoint (TODO: implement)
POST /api/v1/admin/acquisition/jobs/{job_id}/trigger
```

***REMOVED******REMOVED******REMOVED*** Option B: Background Task (Local Dev - with warnings)

For local development, jobs can execute via FastAPI BackgroundTasks (with warnings).

**WARNING**: Background tasks are only for local dev. Production must use Cloud Run Jobs.

***REMOVED******REMOVED*** Results Hub Integration

Results appear automatically in Results Hub UI:

- **Module Title**: "Business List & Contacts (Web Acquisition)"
- **Coverage Report**: Shows businesses found, contacts found, emails, phones, websites
- **Capped Warning**: Shows if results were capped at 100
- **Download Buttons**: CSV and JSON export

***REMOVED******REMOVED*** Local Testing

***REMOVED******REMOVED******REMOVED*** 1. Start the server

```bash
cd backend
python -m uvicorn src.app:app --reload --host 127.0.0.1 --port 8000
```

**Expected log lines:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

***REMOVED******REMOVED******REMOVED*** 2. Create an acquisition job

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/b2b/acquisition/jobs" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -d '{
    "plan_id": "test_plan_123",
    "target_type": "both",
    "sources_policy": "official_only",
    "max_results": 100
  }'
```

**Expected response:**
```json
{
  "success": true,
  "job_id": "uuid-here",
  "status": "queued"
}
```

***REMOVED******REMOVED******REMOVED*** 3. Check job status

```bash
curl "http://127.0.0.1:8000/api/v1/b2b/acquisition/jobs/{job_id}" \
  -H "X-API-Key: <YOUR_API_KEY>"
```

***REMOVED******REMOVED******REMOVED*** 4. Download results

```bash
***REMOVED*** CSV
curl "http://127.0.0.1:8000/api/v1/b2b/acquisition/jobs/{job_id}/export.csv" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -o results.csv

***REMOVED*** JSON
curl "http://127.0.0.1:8000/api/v1/b2b/acquisition/jobs/{job_id}/export.json" \
  -H "X-API-Key: <YOUR_API_KEY>" \
  -o results.json
```

***REMOVED******REMOVED*** Compliance

***REMOVED******REMOVED******REMOVED*** Cap Enforcement

- **MAX 100 results** per query (enforced automatically)
- Admin override available (up to 1000 via admin API key)
- Capped warning shown in Results Hub UI

***REMOVED******REMOVED******REMOVED*** Blocklist Policy

Restricted domains are automatically blocked:
- No scraping of LinkedIn, Facebook, Twitter, etc.
- No personal/sensitive persona data
- Professional B2B level only (role/department/seniority/buying_committee)

***REMOVED******REMOVED******REMOVED*** Rate Limiting

Per-domain rate limiting:
- 10 requests per minute per domain
- Prevents abuse and respects website resources

***REMOVED******REMOVED*** Database Models

- `acquisition_jobs`: Job tracking
- `acquisition_results`: Individual results (businesses/contacts)
- `evidence_sources`: Source tracking for audit

***REMOVED******REMOVED*** Tests

Run tests:

```bash
cd backend
python -m pytest tests/test_web_acquisition.py -v
```

**Test Coverage:**
- Cap enforcement (max 100)
- Blocklist policy
- Export endpoints return valid files
- Sources policy validation
- Job status transitions

***REMOVED******REMOVED*** Future Enhancements

- [ ] Cloud Run Job trigger endpoint (admin-only)
- [ ] PDF export support
- [ ] Real Stagehand API integration (when enabled)
- [ ] Admin dashboard for job monitoring
- [ ] Webhook notifications on job completion
