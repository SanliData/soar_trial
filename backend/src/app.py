"""
APP: app
PURPOSE: FastAPI application setup with middleware and routes
ENCODING: UTF-8 WITHOUT BOM
"""
from dotenv import load_dotenv
from pathlib import Path

***REMOVED*** Load .env from backend/ before any os.getenv (override=True so .env wins over existing env vars)
_backend_dir = Path(__file__).resolve().parent.parent
load_dotenv(_backend_dir / ".env", override=True)

import asyncio
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.exceptions import RequestValidationError

***REMOVED*** Fail-fast: validate required env for production (raises ValueError if invalid)
from src.config.settings import get_settings
get_settings()

from src.middleware.custom_static_files import NoCacheStaticFiles
from src.middleware.request_id_middleware import RequestIDMiddleware
from src.middleware.security_headers_middleware import SecurityHeadersMiddleware
from src.middleware.rate_limiting_middleware import RateLimitingMiddleware
from src.middleware.bot_defense_middleware import BotDefenseMiddleware
from src.middleware.cache_control_middleware import CacheControlMiddleware
from src.middleware.static_files_cache_middleware import StaticFilesCacheMiddleware

from src.http.v1.router_registry import router as v1_router
from src.http.v1.semantic_capability_router import router as semantic_capability_router
from src.http.v1.semantic_capability_graph_router import router as semantic_capability_graph_router
from src.http.v1.spec_verification_governance_router import router as spec_verification_governance_router
from src.http.v1.evolution_governance_router import router as evolution_governance_router
from src.http.v1.capability_gateway_router import router as capability_gateway_router
from src.http.v1.workspace_protocol_router import router as workspace_protocol_router
from src.http.v1.agent_proxy_firewall_router import router as agent_proxy_firewall_router
from src.http.v1.skill_runtime_router import router as skill_runtime_router
from src.http.v1.inference_runtime_router import router as inference_runtime_router
from src.http.v1.persistent_workspace_router import router as persistent_workspace_router
from src.http.v1.graph_intelligence_router import router as graph_intelligence_router
from src.http.v1.runtime_clustering_router import router as runtime_clustering_router
from src.http.v1.long_context_runtime_router import router as long_context_runtime_router
from src.http.v1.private_runtime_security_router import router as private_runtime_security_router
from src.http.v1.ensemble_governance_router import router as ensemble_governance_router
from src.http.v1.context_orchestration_router import router as context_orchestration_router
from src.http.v1.context_compression_router import router as context_compression_router
from src.http.v1.context_isolation_router import router as context_isolation_router
from src.http.v1.document_intelligence_router import router as document_intelligence_router
from src.http.v1.mcp_runtime_router import router as mcp_runtime_router
from src.http.v1.agent_operating_system_router import router as agent_operating_system_router
from src.http.v1.natural_language_control_plane_router import router as natural_language_control_plane_router
from src.http.v1.federated_retrieval_router import router as federated_retrieval_router
from src.http.v1.selective_context_runtime_router import router as selective_context_runtime_router
from src.http.v1.system_visibility_router import router as system_visibility_router
from src.http.v1.results_hub_router import router as results_hub_router
from src.http.v1.conversational_evaluation_router import router as conversational_evaluation_router
from src.http.v1.generative_operational_ui_router import router as generative_operational_ui_router
from src.http.v1.agui_runtime_router import router as agui_runtime_router
from src.http.v1.hitl_runtime_router import router as hitl_runtime_router
from src.http.v1.agentic_identity_router import router as agentic_identity_router
from src.http.v1.hardware_aware_runtime_router import router as hardware_aware_runtime_router
from src.http.v1.adaptive_clustering_router import router as adaptive_clustering_router
from src.http.v1.prompt_cache_governance_router import router as prompt_cache_governance_router
from src.http.v1.agent_deployment_profiles_router import router as agent_deployment_profiles_router
from src.http.v1.ai_runtime_router import router as ai_runtime_router
from src.http.v1.reflection_optimization_router import router as reflection_optimization_router
from src.http.v1.knowledge_ingestion_router import router as knowledge_ingestion_router
from src.http.v1.intelligence_widget_router import router as intelligence_widget_router
from src.http.v1.commercial_graph_router import router as commercial_graph_router
from src.http.v1.prompt_orchestration_router import router as prompt_orchestration_router
from src.http.v1.trajectory_evaluation_router import router as trajectory_evaluation_router
from src.http.v1.agent_security_router import router as agent_security_router
from src.http.v1.runtime_context_router import router as runtime_context_router
from src.http.v1.agent_harness_router import router as agent_harness_router
from src.http.v1.workflow_governance_router import router as workflow_governance_router
from src.http.v1.reliability_governance_router import router as reliability_governance_router
from src.http.v1.support_router import router as support_router
from src.http.v1.b2b_api_router import router as b2b_api_router
from src.http.v1.plan_router import router as plan_router
from src.http.v1.admin_router import router as admin_router
from src.http.v1.result_router import router as result_router
from src.http.v1.visit_route_router import router as visit_route_router
from src.http.v1.explorer_router import router as explorer_router
from src.http.v1.public_router import router as public_router
from src.http.v1.chat_router import router as chat_router
from src.http.v1.feasibility_router import router as feasibility_router
from src.http.v1.exposure_router import router as exposure_router
from src.http.v1.reachability_router import router as reachability_router
from src.http.v1.generative_ui_router import router as generative_ui_router
from src.http.v1.agents_router import router as agents_router
from src.http.v1.ai_sales_router import router as ai_sales_router
from src.http.v1.learning_router import router as learning_router
from src.http.v1.skills_router import router as skills_router
from src.http.v1.sales_engine_router import router as sales_engine_router
from src.http.v1.monitoring_router import router as monitoring_router
from src.http.export_results_router import router as export_results_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    ***REMOVED*** Ensure log directory exists (PM2 uses ./logs when cwd=backend)
    try:
        (_backend_dir / "logs").mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    ***REMOVED*** Production: do not expose docs by default
    docs_url = "/docs" if settings.ENABLE_DOCS else None
    redoc_url = "/redoc" if settings.ENABLE_DOCS else None
    openapi_url = "/openapi.json" if settings.ENABLE_DOCS else None
    _app_version = (settings.FINDEROS_VERSION or "1.0.0").strip()
    if not _app_version:
        _app_version = "1.0.0"

    app = FastAPI(
        title="FinderOS Backend",
        version=_app_version,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    ***REMOVED*** Log level: INFO in production
    if settings.ENV == "production":
        logging.getLogger().setLevel(logging.INFO)
        for _n in ("uvicorn", "uvicorn.error", "src"):
            logging.getLogger(_n).setLevel(logging.INFO)

    ***REMOVED*** ---------------------------
    ***REMOVED*** Middleware
    ***REMOVED*** ---------------------------
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(StaticFilesCacheMiddleware)
    app.add_middleware(CacheControlMiddleware)
    app.add_middleware(BotDefenseMiddleware)
    app.add_middleware(RateLimitingMiddleware)

    _cors_origins = settings.FINDEROS_CORS_ORIGINS.strip()
    if settings.ENV == "production":
        _origins = [o.strip() for o in _cors_origins.split(",") if o.strip()]
        if not _origins:
            raise ValueError("FINDEROS_CORS_ORIGINS must be set in production (validation should have caught this).")
        ***REMOVED*** Ensure soarb2b.com origins for Google OAuth / frontend
        for origin in ("https://soarb2b.com", "https://www.soarb2b.com"):
            if origin not in _origins:
                _origins.append(origin)
        allow_origins = list(dict.fromkeys(_origins))
        allow_credentials = True
    else:
        allow_origins = ["*"] if not _cors_origins else [o.strip() for o in _cors_origins.split(",") if o.strip()] or ["*"]
        allow_credentials = False
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    ***REMOVED*** ---------------------------
    ***REMOVED*** Root – redirect to UI home
    ***REMOVED*** ---------------------------
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/ui/tr/soarb2b_home.html")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return Response(status_code=204)

    ***REMOVED*** ---------------------------
    ***REMOVED*** Health (API / monitoring)
    ***REMOVED*** ---------------------------
    @app.get("/health", include_in_schema=False)
    async def health():
        return {
            "service": "FinderOS Backend",
            "status": "running",
            "version": settings.FINDEROS_VERSION or "1.0.0",
        }

    ***REMOVED*** ---------------------------
    ***REMOVED*** Legacy Redirects (UI)
    ***REMOVED*** ---------------------------
    @app.get("/ui/soarb2b_home.html")
    async def redirect_home():
        return RedirectResponse("/ui/tr/soarb2b_home.html", status_code=301)

    @app.get("/ui/soarb2b_onboarding_5q.html")
    async def redirect_onboarding():
        return RedirectResponse("/ui/tr/soarb2b_onboarding_5q.html", status_code=301)

    @app.get("/ui/demo_showcase.html")
    async def redirect_demo():
        return RedirectResponse("/ui/tr/demo_showcase.html", status_code=301)

    @app.get("/healthz")
    def healthz():
        """Liveness: app running, DB connect, Redis (connected / disabled / failed)."""
        out = {"status": "ok", "checks": {"app": "ok"}}
        try:
            from sqlalchemy import text
            from src.db.base import engine
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            out["checks"]["database"] = "ok"
        except Exception as e:
            logger.warning("Healthz DB check failed: %s", e)
            out["checks"]["database"] = "error"
            out["status"] = "degraded"
        try:
            from src.middleware.rate_limit_redis import get_redis_client
            r = get_redis_client()
            if r is None:
                out["checks"]["redis"] = "disabled"
            else:
                r.ping()
                out["checks"]["redis"] = "connected"
        except Exception:
            out["checks"]["redis"] = "failed"
            if get_settings().REDIS_REQUIRED:
                out["status"] = "degraded"
        return out

    @app.get("/readyz")
    def readyz():
        """Readiness: critical services (DB) must be up."""
        try:
            from sqlalchemy import text
            from src.db.base import engine
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return {"status": "ok", "ready": True}
        except Exception as e:
            logger.warning("Readyz DB check failed: %s", e)
            raise HTTPException(status_code=503, detail="Database not ready")

    ***REMOVED*** ---------------------------
    ***REMOVED*** Routers
    ***REMOVED*** ---------------------------
    app.include_router(v1_router)
    app.include_router(semantic_capability_router, prefix="/api/v1")
    app.include_router(semantic_capability_graph_router, prefix="/api/v1")
    app.include_router(spec_verification_governance_router, prefix="/api/v1")
    app.include_router(evolution_governance_router, prefix="/api/v1")
    app.include_router(capability_gateway_router, prefix="/api/v1")
    app.include_router(workspace_protocol_router, prefix="/api/v1")
    app.include_router(agent_proxy_firewall_router, prefix="/api/v1")
    app.include_router(skill_runtime_router, prefix="/api/v1")
    app.include_router(inference_runtime_router, prefix="/api/v1")
    app.include_router(persistent_workspace_router, prefix="/api/v1")
    app.include_router(graph_intelligence_router, prefix="/api/v1")
    app.include_router(runtime_clustering_router, prefix="/api/v1")
    app.include_router(long_context_runtime_router, prefix="/api/v1")
    app.include_router(private_runtime_security_router, prefix="/api/v1")
    app.include_router(ensemble_governance_router, prefix="/api/v1")
    app.include_router(context_orchestration_router, prefix="/api/v1")
    app.include_router(context_compression_router, prefix="/api/v1")
    app.include_router(context_isolation_router, prefix="/api/v1")
    app.include_router(document_intelligence_router, prefix="/api/v1")
    app.include_router(mcp_runtime_router, prefix="/api/v1")
    app.include_router(agent_operating_system_router, prefix="/api/v1")
    app.include_router(natural_language_control_plane_router, prefix="/api/v1")
    app.include_router(federated_retrieval_router, prefix="/api/v1")
    app.include_router(selective_context_runtime_router, prefix="/api/v1")
    app.include_router(system_visibility_router, prefix="/api/v1")
    app.include_router(results_hub_router, prefix="/api/v1")
    app.include_router(conversational_evaluation_router, prefix="/api/v1")
    app.include_router(generative_operational_ui_router, prefix="/api/v1")
    app.include_router(agui_runtime_router, prefix="/api/v1")
    app.include_router(hitl_runtime_router, prefix="/api/v1")
    app.include_router(agentic_identity_router, prefix="/api/v1")
    app.include_router(hardware_aware_runtime_router, prefix="/api/v1")
    app.include_router(adaptive_clustering_router, prefix="/api/v1")
    app.include_router(prompt_cache_governance_router, prefix="/api/v1")
    app.include_router(agent_deployment_profiles_router, prefix="/api/v1")
    app.include_router(ai_runtime_router, prefix="/api/v1")
    app.include_router(reflection_optimization_router, prefix="/api/v1")
    app.include_router(knowledge_ingestion_router, prefix="/api/v1")
    app.include_router(intelligence_widget_router, prefix="/api/v1")
    app.include_router(commercial_graph_router, prefix="/api/v1")
    app.include_router(prompt_orchestration_router, prefix="/api/v1")
    app.include_router(trajectory_evaluation_router, prefix="/api/v1")
    app.include_router(agent_security_router, prefix="/api/v1")
    app.include_router(runtime_context_router, prefix="/api/v1")
    app.include_router(agent_harness_router, prefix="/api/v1")
    app.include_router(workflow_governance_router, prefix="/api/v1")
    app.include_router(reliability_governance_router, prefix="/api/v1")
    app.include_router(support_router, prefix="/api/v1")
    app.include_router(b2b_api_router, prefix="/api/v1/b2b")
    app.include_router(plan_router, prefix="/api/v1/b2b")
    app.include_router(admin_router, prefix="/api/v1")
    app.include_router(result_router, prefix="/api/v1/b2b")
    app.include_router(generative_ui_router, prefix="/api/v1/b2b")
    app.include_router(visit_route_router, prefix="/api/v1/b2b")
    app.include_router(explorer_router, prefix="/api/v1")
    app.include_router(public_router, prefix="/api/v1/public")
    app.include_router(chat_router)
    app.include_router(feasibility_router, prefix="/api/v1/b2b")
    app.include_router(exposure_router, prefix="/api/v1/b2b")
    app.include_router(reachability_router, prefix="/api/v1/b2b")
    app.include_router(agents_router)
    app.include_router(ai_sales_router)
    app.include_router(learning_router)
    app.include_router(skills_router)
    app.include_router(sales_engine_router)
    app.include_router(monitoring_router)
    app.include_router(export_results_router)

    ***REMOVED*** ---------------------------
    ***REMOVED*** Static Mount
    ***REMOVED*** ---------------------------
    src_dir = os.path.abspath(os.path.dirname(__file__))
    ui_dir = os.path.join(src_dir, "ui")

    if os.path.exists(ui_dir):
        app.mount("/ui", NoCacheStaticFiles(directory=ui_dir, html=True), name="ui")
        logger.info("UI mounted from %s", ui_dir)
    else:
        logger.warning("UI directory not found: %s", ui_dir)

    ***REMOVED*** ---------------------------
    ***REMOVED*** Global Exception Handler (no stack trace in production)
    ***REMOVED*** ---------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled error", exc_info=True)
        if isinstance(exc, HTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail}
            )
        if isinstance(exc, RequestValidationError):
            return JSONResponse(
                status_code=422,
                content={"detail": exc.errors()}
            )
        detail = "Internal server error"
        if get_settings().ENV != "production":
            detail = f"{type(exc).__name__}: {exc!s}"
        return JSONResponse(
            status_code=500,
            content={"detail": detail}
        )

    ***REMOVED*** ---------------------------
    ***REMOVED*** Startup: config log + REDIS_REQUIRED check
    ***REMOVED*** ---------------------------
    @app.on_event("startup")
    async def startup_config_and_redis():
        s = get_settings()
        ***REMOVED*** Build intelligence graph (schema -> nodes/edges) for NL analytics; cache in memory/Redis
        try:
            import src.models  ***REMOVED*** ensure all tables registered with Base.metadata
            from src.db.base import init_db
            init_db()
            logger.info("database tables initialized")
        except Exception as e:
            logger.warning("database init at startup failed: %s", e)
        try:
            from src.intelligence_graph.graph_worker import enqueue_graph_rebuild, run_graph_worker_loop
            enqueue_graph_rebuild()
            asyncio.create_task(run_graph_worker_loop(interval_seconds=10.0))
            logger.info("intelligence graph rebuild enqueued; background worker started")
        except Exception as e:
            logger.debug("intelligence graph enqueue at startup skipped: %s", e)
        ***REMOVED*** Log env verification (masked secrets)
        cid = (s.GOOGLE_CLIENT_ID or "").strip()
        if cid:
            masked = cid[:8] + "..." + cid[-4:] if len(cid) > 12 else "***"
            logger.info("startup base_url=%s google_client_id=%s", s.BASE_URL or "(not set)", masked)
        else:
            logger.warning("startup base_url=%s google_client_id=missing", s.BASE_URL or "(not set)")
        if s.ENV == "production" and s.BASE_URL:
            logger.info("startup production BASE_URL=%s", s.BASE_URL)
        if s.ENV != "production" or not s.REDIS_REQUIRED:
            return
        try:
            from src.middleware.rate_limit_redis import get_redis_client
            r = get_redis_client()
            if r is None:
                raise ValueError("REDIS_REQUIRED=true but Redis client is not available.")
            r.ping()
        except Exception as e:
            raise RuntimeError(f"REDIS_REQUIRED=true but Redis check failed: {e}") from e
        ***REMOVED*** Optional: start monitoring agent scheduler (every 5 min when MONITORING_AGENT_ENABLED=true)
        try:
            from src.monitoring.scheduler import start_scheduler
            start_scheduler()
        except Exception as e:
            logger.debug("monitoring scheduler not started: %s", e)

    return app


app = create_app()
