***REMOVED*** Deprecated: legacy B2B API routers

**Status:** These routers are **not** included in the main FastAPI app (`src.app:app`).

The active B2B API is under `backend/src/http/v1/` (e.g. `b2b_api_router`, `plan_router`, `result_router`, etc.) and is mounted at `/api/v1/b2b` in `src/app.py`.

Routers in this directory (`backend/api/v1/`):

- `b2b_products_router.py`
- `b2b_personas_router.py`
- `b2b_companies_router.py`
- `b2b_mobile_targeting_router.py`
- `b2b_campaigns_router.py`
- `b2b_appointments_router.py`

**Action:** Either remove these files if unused, or integrate them into `src.http.v1` and include them in `router_registry` / `app.py` when the feature is needed.
