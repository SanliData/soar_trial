***REMOVED*** SOAR B2B - Deployment Runbook

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** Local Development
```powershell
cd backend
.\scripts\run_local.ps1
```

Access UI: http://127.0.0.1:8000/ui/soarb2b_home.html

***REMOVED******REMOVED******REMOVED*** Production Deployment (Docker)
```powershell
cd backend
docker-compose up --build -d
```

***REMOVED******REMOVED******REMOVED*** Production Deployment (Manual)
```powershell
cd backend
$env:ENV="production"
$env:PORT="8000"
$env:SOARB2B_API_KEYS="prod-key-1,prod-key-2"
$env:FINDEROS_CORS_ORIGINS="https://soarb2b.com"
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000
```

---

***REMOVED******REMOVED*** Environment Variables

***REMOVED******REMOVED******REMOVED*** Required (Production)
- `ENV=production`
- `PORT=8000` (or platform-specific PORT)
- `SOARB2B_API_KEYS=key1,key2,key3` (comma-separated)
- `FINDEROS_CORS_ORIGINS=https://yourdomain.com` (comma-separated)

***REMOVED******REMOVED******REMOVED*** Optional
- `FINDEROS_HOST=0.0.0.0`
- `FINDEROS_PORT=8000`
- `DATABASE_URL=postgresql://...` (for future DB migration)

***REMOVED******REMOVED******REMOVED*** Local Development
- No env vars required (uses defaults)
- Default API key: `dev-key-12345` (auto-created)

---

***REMOVED******REMOVED*** Verification Commands

***REMOVED******REMOVED******REMOVED*** Health Checks
```powershell
***REMOVED*** Basic health
Invoke-WebRequest http://127.0.0.1:8000/healthz -UseBasicParsing

***REMOVED*** Readiness
Invoke-WebRequest http://127.0.0.1:8000/readyz -UseBasicParsing

***REMOVED*** Metrics
Invoke-WebRequest http://127.0.0.1:8000/metrics -UseBasicParsing
```

***REMOVED******REMOVED******REMOVED*** API Test
```powershell
$headers = @{"X-API-Key" = "dev-key-12345"}
Invoke-WebRequest http://127.0.0.1:8000/api/v1/b2b/demo/hotels -Headers $headers -UseBasicParsing
```

***REMOVED******REMOVED******REMOVED*** UI Pages
- http://127.0.0.1:8000/ui/soarb2b_home.html
- http://127.0.0.1:8000/ui/soarb2b_onboarding_5q.html
- http://127.0.0.1:8000/ui/demo_showcase.html
- http://127.0.0.1:8000/ui/case_library_index.html

---

***REMOVED******REMOVED*** Troubleshooting

***REMOVED******REMOVED******REMOVED*** Port Already in Use
```powershell
***REMOVED*** Windows: Find process using port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object -ExpandProperty OwningProcess

***REMOVED*** Kill process
Stop-Process -Id <PID>
```

***REMOVED******REMOVED******REMOVED*** API Key Not Working
- Check `backend/data/dev_api_keys.txt` exists
- Default key: `dev-key-12345`
- Set `SOARB2B_API_KEYS` env var for custom keys

***REMOVED******REMOVED******REMOVED*** UI Files Not Loading
- Verify `backend/src/ui/` directory exists
- Check server logs for "Static files mounted" message
- Access via `/ui/` prefix: `http://localhost:8000/ui/soarb2b_home.html`

---

***REMOVED******REMOVED*** Scaling Considerations

***REMOVED******REMOVED******REMOVED*** Current Limits (P0)
- Rate limiting: In-memory (resets on restart)
- Data storage: File-based (JSONL for plans)
- Concurrent users: Single instance

***REMOVED******REMOVED******REMOVED*** For 10k Users (P1/P2)
- Move rate limiting to Redis
- Move data to PostgreSQL
- Add load balancer
- Use async task queue (Celery/RQ)
- Add caching layer (Redis)
- Horizontal scaling with multiple instances

---

**Last Updated:** 2025-01-15
