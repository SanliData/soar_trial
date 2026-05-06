***REMOVED*** SoarB2B Backend — Production Deploy

***REMOVED******REMOVED*** Prerequisites

- Python 3.10+ with venv
- Node.js (for PM2)
- PostgreSQL (production)
- Redis (recommended for rate limit/cache)
- Nginx (reverse proxy)
- Domain + Cloudflare (optional)

***REMOVED******REMOVED*** Directory layout (server)

```
/var/www/finder_os/
├── backend/           ***REMOVED*** repo backend/
│   ├── .env           ***REMOVED*** DO NOT commit; create from .env.example
│   ├── src/
│   └── ...
├── venv/              ***REMOVED*** Python virtualenv
└── logs/              ***REMOVED*** PM2 logs (create if missing)
```

***REMOVED******REMOVED*** 1. Clone and venv

```bash
cd /var/www/finder_os/backend
python3 -m venv /var/www/finder_os/venv
source /var/www/finder_os/venv/bin/activate
pip install -r requirements.txt
```

***REMOVED******REMOVED*** 2. Environment

```bash
cp .env.example .env
***REMOVED*** Edit .env and set at least:
***REMOVED***   ENV=production
***REMOVED***   DATABASE_URL=postgresql://user:pass@host:5432/dbname
***REMOVED***   JWT_SECRET=<strong-secret>
***REMOVED***   SOARB2B_API_KEYS=<comma-separated-api-keys>
***REMOVED***   FINDEROS_CORS_ORIGINS=https://soarb2b.com,https://www.soarb2b.com
```

Production startup will **fail** if `ENV=production` and any of these is missing or invalid:

- `DATABASE_URL` (must be PostgreSQL, no SQLite)
- `JWT_SECRET`
- `SOARB2B_API_KEYS`
- `FINDEROS_CORS_ORIGINS` (comma-separated origins; wildcard not allowed)

Optional: `REDIS_REQUIRED=true` to fail startup when Redis is unavailable; `ENABLE_DOCS=false` to disable `/docs` and `/openapi.json`.

***REMOVED******REMOVED*** 3. PM2

Log directory: PM2 uses `./logs` relative to `cwd` (backend). The app also tries to create `backend/logs` on startup. Verify after first start:

```bash
ls -la /var/www/finder_os/backend/logs
***REMOVED*** or if cwd is repo root: ls -la backend/logs
```

If missing, create manually: `mkdir -p backend/logs` (from repo root) or `mkdir -p ./logs` (from backend).

Start:

```bash
cd /var/www/finder_os/backend
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup   ***REMOVED*** optional: start on boot
```

Check:

```bash
pm2 status
pm2 logs soarb2b
curl -s http://127.0.0.1:8000/healthz
curl -s http://127.0.0.1:8000/readyz
```

`ecosystem.config.cjs` uses:

- **cwd:** `/var/www/finder_os/backend`
- **script:** `/var/www/finder_os/venv/bin/python3`
- **args:** `-m uvicorn src.app:app --host 0.0.0.0 --port 8000`
- **autorestart**, **max_restarts**, **error_file**, **out_file**

If you deploy to a different path, update `cwd`, `script`, `error_file`, and `out_file` in `ecosystem.config.cjs`.

***REMOVED******REMOVED*** 4. Nginx

Use the example config: `deploy/nginx.example.conf` (80→443 redirect, proxy to 127.0.0.1:8000, `client_max_body_size`, gzip, no-cache for API paths). Copy and adjust `server_name` and SSL paths, then:

```bash
sudo nginx -t && sudo systemctl reload nginx
```

***REMOVED******REMOVED*** 5. Health endpoints

- **GET /healthz** — Liveness: app + DB connect + optional Redis. Returns 200; may report `"status": "degraded"` if DB fails.
- **GET /readyz** — Readiness: DB must be up. Returns 503 if DB unavailable.

Use these for load balancer or Kubernetes probes.

***REMOVED******REMOVED*** 6. Troubleshooting

| Symptom | Check |
|--------|------|
| App not starting | `pm2 logs soarb2b`; ensure `.env` exists and required vars set; no SQLite when `ENV=production` |
| 502 from Nginx | Backend listening on 8000: `curl -s http://127.0.0.1:8000/healthz` |
| 503 readyz | DB connection: `DATABASE_URL`, PostgreSQL reachable, firewall |
| CORS errors | Set `FINDEROS_CORS_ORIGINS` to comma-separated frontend origins |
