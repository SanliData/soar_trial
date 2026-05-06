"""
ROUTER: b2b_api_router
PURPOSE: SOAR B2B API endpoints for onboarding, case library, and demo data
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import json
import uuid
import time
import logging
import requests
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Request, Query, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.db.base import get_db
from src.services.auth_service import get_email_from_jwt, is_admin_email

# Cache imports
from src.core.cache import get_cache, set_cache, cache_key

# Feasibility service import
from src.services.feasibility_service import get_feasibility_service
from src.services.plan_service import get_plan_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
CASE_LIBRARY_DIR = Path(__file__).parent.parent.parent / "ui" / "case_library"
DATA_DIR.mkdir(exist_ok=True)

# In-memory cache for case library files (TTL: 60 seconds)
_case_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
CACHE_TTL = 60.0


def _load_case_file(case_file: Path) -> Optional[Dict[str, Any]]:
    """Load case file with caching"""
    cache_key = str(case_file)
    current_time = time.time()
    
    # Check cache
    if cache_key in _case_cache:
        cached_data, cached_time = _case_cache[cache_key]
        if current_time - cached_time < CACHE_TTL:
            return cached_data
    
    # Load from disk
    try:
        case_data = json.loads(case_file.read_text(encoding="utf-8"))
        _case_cache[cache_key] = (case_data, current_time)
        return case_data
    except Exception:
        return None


def _get_all_cases() -> List[Dict[str, Any]]:
    """Load all case files from library directory"""
    cases = []
    
    if not CASE_LIBRARY_DIR.exists():
        return cases
    
    for case_file in CASE_LIBRARY_DIR.glob("*.json"):
        if case_file.name == "template.json":
            continue
        
        case_data = _load_case_file(case_file)
        if case_data:
            cases.append(case_data)
    
    return cases


# API Key Authentication
def get_api_key(request: Request) -> Optional[str]:
    """Extract API key from X-API-Key header"""
    api_key = request.headers.get("X-API-Key")
    return api_key


def validate_api_key(api_key: Optional[str] = Depends(get_api_key)) -> str:
    """Validate API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    
    # Trim received API key to handle any whitespace issues
    api_key = api_key.strip()
    
    # Debug logging (masked for security)
    masked_key = f"{api_key[:5]}***{api_key[-5:]}" if len(api_key) > 10 else "***"
    logger.info(f"API KEY RECEIVED: {masked_key} (length: {len(api_key)})")
    
    # Load allowed keys from env or dev file
    allowed_keys_env = os.getenv("SOARB2B_API_KEYS", "")
    # Ensure keys are trimmed - split by comma and strip whitespace
    allowed_keys = [k.strip() for k in allowed_keys_env.split(",") if k.strip()]
    
    # Debug logging
    logger.info(f"ALLOWED KEYS COUNT: {len(allowed_keys)}")
    if allowed_keys:
        masked_allowed = [f"{k[:5]}***{k[-5:]}" if len(k) > 10 else "***" for k in allowed_keys]
        logger.info(f"ALLOWED KEYS (masked): {masked_allowed}")
    
    # Dev fallback - always check file even if env var had some keys
    # This allows adding keys to file without restarting server
    dev_key_file = DATA_DIR / "dev_api_keys.txt"
    logger.info(f"Checking API key file: {dev_key_file} (exists: {dev_key_file.exists()})")
    if dev_key_file.exists():
        try:
            file_content = dev_key_file.read_text(encoding="utf-8")
            file_keys = [k.strip() for k in file_content.splitlines() if k.strip()]
            logger.info(f"Read {len(file_keys)} keys from file: {[f'{k[:5]}***' if len(k) > 10 else k for k in file_keys]}")
            # Merge env keys with file keys (deduplicate)
            allowed_keys = list(set(allowed_keys + file_keys))
            logger.info(f"Loaded {len(file_keys)} keys from file, total allowed: {len(allowed_keys)}")
        except Exception as e:
            logger.error(f"Failed to read dev_api_keys.txt: {e}", exc_info=True)
    elif not allowed_keys:
        # Create default dev key only if no keys from env and file doesn't exist
        default_key = "dev-key-12345"
        dev_key_file.write_text(default_key)
        allowed_keys = [default_key]
    
    # Debug: Log comparison details
    logger.info(f"Validating key (length {len(api_key)}) against {len(allowed_keys)} allowed keys")
    logger.debug(f"Received key (first 10 chars): {api_key[:10]}...")
    if allowed_keys:
        logger.debug(f"Allowed keys (first 10 chars each): {[k[:10] for k in allowed_keys[:3]]}")
    
    if api_key not in allowed_keys:
        logger.warning(f"API KEY VALIDATION FAILED: {masked_key} not in allowed keys (checked {len(allowed_keys)} keys)")
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    logger.info(f"API KEY VALIDATED SUCCESSFULLY: {masked_key}")
    return api_key


def validate_api_key_or_jwt(
    http_request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> str:
    """
    Accept either valid X-API-Key or valid JWT (Authorization: Bearer).
    Used for create-plan so browser users can call with their login token.
    """
    api_key = get_api_key(http_request)
    if api_key:
        try:
            return validate_api_key(api_key)
        except HTTPException:
            pass   # fall through to JWT
    if authorization and authorization.strip().lower().startswith("bearer "):
        email = get_email_from_jwt(authorization)
        if email:
            logger.info(f"create-plan auth: JWT valid for {email}")
            return "jwt"
    raise HTTPException(status_code=403, detail="Invalid API key")


# Request Models
class OnboardingRequest(BaseModel):
    target_type: str = Field(..., description="Type of businesses to target")
    geography: str = Field(..., description="Target locations")
    decision_roles: str = Field(..., description="Decision-maker roles")
    product_service: str = Field(..., description="Product or service description")
    meeting_goal: str = Field(..., description="Meeting objective")
    zip_code: Optional[str] = Field(None, description="ZIP/Postal code for targeting")
    radius_miles: Optional[str] = Field(None, description="Radius in miles for geo-targeting")
    selected_lat: Optional[float] = Field(None, description="Selected latitude from map")
    selected_lng: Optional[float] = Field(None, description="Selected longitude from map")
    auto_start_queries: bool = Field(default=False, description="Start analysis automatically after submission (Yes/No)")
    quote_token: Optional[str] = Field(None, description="Signed quote token from /pricing/calculate endpoint (required if auto_start_queries=True)")
    include_persona_deepening: bool = Field(default=False, description="Include persona deepening module")
    include_visit_route: bool = Field(default=False, description="Include visit route module")
    include_export: bool = Field(default=False, description="Include export module")
    include_outreach_preparation: bool = Field(default=False, description="Include outreach preparation module")
    max_results: int = Field(default=100, description="Maximum results (max: 100)")
    hs_code: Optional[str] = Field(None, description="HS / gümrük kodu (zorunlu arşiv; girilmezse AI ile eklenir)")
    user_id: Optional[int] = Field(None, description="Kullanıcı ID (giriş yapmışsa; geçmiş arşivde görünsün)")
    linkedin_upload_id: Optional[str] = Field(None, description="Upload ID from /api/v1/public/upload/linkedin-profile (persona seed)")
    company_upload_id: Optional[str] = Field(None, description="Upload ID from /api/v1/public/upload/company-target (company seed)")


class OnboardingPlanResponse(BaseModel):
    plan_id: str
    target_type: str
    geography: str
    decision_roles: str
    product_service: str
    meeting_goal: str
    created_at: str
    recommendations: Dict[str, Any]


# --- PlanSpec: single contract for Assistant / GPT integration ---
class RegionSpec(BaseModel):
    type: str = Field(..., description="city | state | radius")
    value: str = Field(..., description="e.g. Istanbul, California, or 25")


class LimitsSpec(BaseModel):
    company_limit: int = Field(default=100, ge=1, le=100, description="Max companies (capped 100)")
    company_size_max: Optional[int] = Field(default=50, description="UPAP: max employees per company")
    min_ready_leads: Optional[int] = Field(default=5, description="UPAP: min ready leads for export")


class FlagsSpec(BaseModel):
    simulation_mode: bool = Field(default=False, description="Simulation / demo mode")
    regulated_domain: bool = Field(default=False, description="Regulated industry (UPAP)")


class TargetsSpec(BaseModel):
    primary_goal: str = Field(default="meetings", description="meetings | awareness | pipeline")


class PlanSpec(BaseModel):
    """Single contract for GPT/Assistant → Plan → Run → Results. Unlocks pricing, preview, UPAP, export."""
    product: str = Field(..., description="Product or service description")
    region: RegionSpec = Field(..., description="Target geography (city/state/radius)")
    modules: List[str] = Field(
        default_factory=lambda: ["discovery", "persona"],
        description="discovery, persona, exposure, soft_conversion, outreach, visit_route"
    )
    limits: Optional[LimitsSpec] = Field(default_factory=LimitsSpec)
    flags: Optional[FlagsSpec] = Field(default_factory=FlagsSpec)
    targets: Optional[TargetsSpec] = Field(default_factory=TargetsSpec)
    # Optional: explicit mapping to onboarding fields (if GPT provides them)
    target_type: Optional[str] = Field(None, description="Type of businesses (default derived from product)")
    decision_roles: Optional[str] = Field(None, description="Decision-maker roles (default: Decision makers)")


class PlanSpecCreatePlanResponse(BaseModel):
    plan_id: str
    created_at: str
    message: str = "Plan created from PlanSpec. Use preview-scope then start-run."


class PreviewScopeResponse(BaseModel):
    plan_id: str
    estimated_total: int = Field(..., description="Total companies in scope")
    sample_100: int = Field(..., description="Sample size (capped 100)")
    warnings: Optional[List[str]] = Field(None, description="e.g. region too large, cap applied")
    target_region: str = ""


class StartRunRequest(BaseModel):
    plan_id: str = Field(..., description="Plan ID from create-plan")
    quote_token: Optional[str] = Field(None, description="From pricing/calculate if cost confirmation required")


class StartRunResponse(BaseModel):
    success: bool
    plan_id: str
    run_id: Optional[str] = None
    status: str = ""
    message: str = ""
    requires_cost_confirmation: bool = False
    cost_preview: Optional[Dict[str, Any]] = None


def _plan_spec_to_onboarding_request(spec: PlanSpec, plan_id: str) -> OnboardingRequest:
    """Map PlanSpec to OnboardingRequest for existing create-plan flow."""
    geography = spec.region.value
    if spec.region.type == "radius" and spec.region.value.isdigit():
        radius_miles = spec.region.value
        geography = f"Radius {spec.region.value} miles"
    else:
        radius_miles = None
    meeting_goal_map = {"meetings": "1", "awareness": "2", "pipeline": "3"}
    goal = (spec.targets or TargetsSpec()).primary_goal
    meeting_goal = meeting_goal_map.get(goal, "1")
    target_type = spec.target_type or f"B2B companies for {spec.product[:50]}"
    decision_roles = spec.decision_roles or "Decision makers"
    limits = spec.limits or LimitsSpec()
    return OnboardingRequest(
        target_type=target_type,
        geography=geography,
        decision_roles=decision_roles,
        product_service=spec.product,
        meeting_goal=meeting_goal,
        zip_code=None,
        radius_miles=radius_miles,
        selected_lat=None,
        selected_lng=None,
        auto_start_queries=False,
        quote_token=None,
        include_persona_deepening="persona" in (spec.modules or []),
        include_visit_route="visit_route" in (spec.modules or []),
        include_export=True,
        include_outreach_preparation="outreach" in (spec.modules or []),
        max_results=min(limits.company_limit, 100),
        hs_code=None,
        user_id=None,
        linkedin_upload_id=None,
        company_upload_id=None,
    )


# Endpoints
@router.post("/onboarding/create-plan", response_model=OnboardingPlanResponse)
async def create_onboarding_plan(
    request: OnboardingRequest,
    http_request: Request,
    api_key: str = Depends(validate_api_key_or_jwt),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Create a meeting plan from onboarding answers.
    Results are cached by plan_id for 1 hour.
    """
    plan_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    # Check cache first (by plan_id if exists)
    plan_cache_key = cache_key("plan", plan_id=plan_id)
    cached_plan = get_cache(plan_cache_key)
    if cached_plan is not None:
        logger.debug(f"Cache hit: plan:{plan_id}")
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=cached_plan)
        response.headers["X-Cache"] = "HIT"
        return OnboardingPlanResponse(**cached_plan)
    
    logger.debug(f"Cache miss: plan:{plan_id}")
    
    # Generate recommendations
    recommendations = {
        "sequence": [
            "Target List Creation",
            "Decision-Maker Focus",
            "Precision Exposure",
            "Platform Expansion",
            "Direct Access"
        ],
        "first_actions": [
            f"Create verified target list: {request.target_type} in {request.geography}",
            f"Set up role targeting: {request.decision_roles}",
            f"Launch precision exposure campaign for {request.target_type}"
        ],
        "estimated_timeframe_days": {
            "min": 30,
            "max": 60
        }
    }
    
    plan_data = {
        "plan_id": plan_id,
        "target_type": request.target_type,
        "geography": request.geography,
        "decision_roles": request.decision_roles,
        "product_service": request.product_service,
        "meeting_goal": request.meeting_goal,
        "zip_code": request.zip_code,
        "radius_miles": request.radius_miles,
        "selected_lat": request.selected_lat,
        "selected_lng": request.selected_lng,
        "auto_start_queries": request.auto_start_queries,
        "created_at": created_at,
        "recommendations": recommendations
    }
    if request.linkedin_upload_id:
        plan_data["linkedin_upload_id"] = request.linkedin_upload_id
    if request.company_upload_id:
        plan_data["company_upload_id"] = request.company_upload_id
    
    # Onboarding data: always include HS/gümrük kodu (user or AI) for archive
    onboarding_data = {
        "target_type": request.target_type,
        "geography": request.geography,
        "decision_roles": request.decision_roles,
        "product_service": request.product_service,
        "meeting_goal": request.meeting_goal,
        "zip_code": request.zip_code,
        "radius_miles": request.radius_miles,
        "selected_lat": request.selected_lat,
        "selected_lng": request.selected_lng,
        "auto_start_queries": request.auto_start_queries,
    }
    if request.linkedin_upload_id:
        onboarding_data["linkedin_upload_id"] = request.linkedin_upload_id
    if request.company_upload_id:
        onboarding_data["company_upload_id"] = request.company_upload_id
    if request.hs_code and (request.hs_code or "").strip():
        onboarding_data["hs_code"] = (request.hs_code or "").strip()
        onboarding_data["hs_code_source"] = "user"
        onboarding_data["product_customs_description"] = f"User-provided HS {request.hs_code}"
    from src.services.hs_code_service import ensure_hs_code_in_onboarding
    onboarding_data = ensure_hs_code_in_onboarding(onboarding_data)
    plan_data["hs_code"] = onboarding_data.get("hs_code")
    plan_data["hs_code_source"] = onboarding_data.get("hs_code_source")
    plan_data["product_customs_description"] = onboarding_data.get("product_customs_description")
    
    # Store plan (P0: file-based, P1: DB)
    plans_file = DATA_DIR / "onboarding_plans.jsonl"
    with open(plans_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(plan_data, ensure_ascii=False) + "\n")
    
    # Kullanıcı ilişkisi: request.user_id veya X-User-Id header (geçmiş arşiv için)
    created_by_user_id = request.user_id
    if created_by_user_id is None:
        try:
            uid = http_request.headers.get("X-User-Id")
            created_by_user_id = int(uid) if uid else None
        except (TypeError, ValueError):
            created_by_user_id = None
    # Create PlanLifecycle (first-class Plan object)
    try:
        plan_service = get_plan_service(db)
        plan_service.create_plan_lifecycle(plan_id, onboarding_data, created_by_user_id=created_by_user_id)
        logger.info(f"Plan lifecycle created for plan: {plan_id}")
    except Exception as e:
        # Don't fail onboarding if lifecycle creation fails
        logger.warning(f"Plan lifecycle creation skipped: {str(e)}")
    
    # Cache plan (TTL: 1 hour = 3600 seconds)
    set_cache(plan_cache_key, plan_data, ttl=3600)
    
    # Auto-start queries if user opted in
    if request.auto_start_queries:
        # Admin users (e.g. isanli058@gmail.com) skip payment/quote_token requirement
        admin_email = get_email_from_jwt(authorization)
        is_admin = is_admin_email(admin_email)
        cost_confirmed = is_admin
        if is_admin:
            logger.info(f"Admin user {admin_email!r}: skipping quote_token for plan {plan_id}")

        if not is_admin:
            # HARD ENFORCEMENT: Require valid quote_token for non-admin users
            if not request.quote_token:
                logger.warning(f"Query execution blocked for plan {plan_id}: quote_token missing")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "quote_token is required for query execution",
                        "error_code": "QUOTE_TOKEN_MISSING",
                        "message": "Please call /v1/subscriptions/pricing/calculate first to get a quote_token"
                    }
                )

            # Validate quote token
            try:
                from src.core.quote_token import validate_quote_token
                from src.core.query_limits import MAX_RESULTS_PER_QUERY

                # Enforce max_results cap
                normalized_max_results = min(request.max_results, MAX_RESULTS_PER_QUERY)

                validation_result = validate_quote_token(
                    quote_token=request.quote_token,
                    include_persona_deepening=request.include_persona_deepening,
                    include_visit_route=request.include_visit_route,
                    include_export=request.include_export,
                    include_outreach_preparation=request.include_outreach_preparation,
                    max_results=normalized_max_results
                )

                if not validation_result["valid"]:
                    logger.warning(f"Query execution blocked for plan {plan_id}: {validation_result['error_code']} - {validation_result['error']}")
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": validation_result["error"],
                            "error_code": validation_result["error_code"],
                            "message": "Quote token validation failed. Please get a new quote from /v1/subscriptions/pricing/calculate"
                        }
                    )

                cost_confirmed = True
                logger.info(f"Quote token validated for plan {plan_id}, proceeding with query execution")

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error validating quote token: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": f"Error validating quote token: {str(e)}",
                        "error_code": "QUOTE_TOKEN_VALIDATION_ERROR"
                    }
                )

        try:
            from src.services.query_execution_service import get_query_execution_service
            query_service = get_query_execution_service(db)
            # Start query pipeline automatically (no admin approval needed for standard queries)
            # MAX 100 results enforced automatically
            query_service.start_query_pipeline(
                plan_id=plan_id,
                target_type=request.target_type,
                geography=request.geography,
                decision_roles=request.decision_roles,
                auto_approved=True,   # Standard queries (MAX 100) don't need admin approval
                cost_confirmed=cost_confirmed,
            )
            logger.info(f"Query pipeline auto-started for plan: {plan_id} (cost_confirmed={cost_confirmed})")
        except Exception as e:
            # Don't fail onboarding if query execution fails
            logger.warning(f"Auto-start query pipeline skipped: {str(e)}")
    else:
        logger.info(f"Plan {plan_id} created as draft - awaiting admin review or manual start")
    
    # Generate feasibility report (preview only - aggregated counts)
    # NOTE: This generates aggregated preview data only - no personal identifiers
    # User ID would come from authenticated session in production
    # For now, we use a placeholder (API key-based auth)
    try:
        feasibility_service = get_feasibility_service(db)
        # TODO: Get actual user_id from authentication
        # For now, feasibility report is generated without user association
        # In production, extract user_id from authenticated session
        logger.info(f"Feasibility report generation triggered for plan: {plan_id}")
        # feasibility_service.generate_feasibility_report(
        # user_id=user_id,  # From authenticated session
        # onboarding_plan_id=plan_id,
        # geography=request.geography,
        # target_type=request.target_type,
        # decision_roles=request.decision_roles,
        # region=request.geography
        # )
    except Exception as e:
        # Don't fail onboarding if feasibility report generation fails
        logger.warning(f"Feasibility report generation skipped: {str(e)}")
    
    # Add cache header (MISS for new plan)
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=plan_data)
    response.headers["X-Cache"] = "MISS"
    return response


# --- Assistant / GPT orchestrator endpoints (PlanSpec → Plan → Run → Results) ---

@router.post("/assistant/create-plan", response_model=PlanSpecCreatePlanResponse)
async def assistant_create_plan(
    spec: PlanSpec,
    http_request: Request,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    """
    Create a plan from PlanSpec (GPT/Assistant output).
    Single contract: pricing, preview, UPAP gates, and export all consume this.
    """
    onboarding_request = _plan_spec_to_onboarding_request(spec, "")
    plan_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    recommendations = {
        "sequence": ["Target List", "Decision-Maker Focus", "Precision Exposure", "Platform Expansion", "Direct Access"],
        "first_actions": [
            f"Create target list: {onboarding_request.target_type} in {onboarding_request.geography}",
            f"Set role targeting: {onboarding_request.decision_roles}",
        ],
        "estimated_timeframe_days": {"min": 30, "max": 60},
    }
    plan_data = {
        "plan_id": plan_id,
        "target_type": onboarding_request.target_type,
        "geography": onboarding_request.geography,
        "decision_roles": onboarding_request.decision_roles,
        "product_service": onboarding_request.product_service,
        "meeting_goal": onboarding_request.meeting_goal,
        "zip_code": onboarding_request.zip_code,
        "radius_miles": onboarding_request.radius_miles,
        "selected_lat": onboarding_request.selected_lat,
        "selected_lng": onboarding_request.selected_lng,
        "auto_start_queries": False,
        "created_at": created_at,
        "recommendations": recommendations,
    }
    onboarding_data = {
        "target_type": onboarding_request.target_type,
        "geography": onboarding_request.geography,
        "decision_roles": onboarding_request.decision_roles,
        "product_service": onboarding_request.product_service,
        "meeting_goal": onboarding_request.meeting_goal,
        "zip_code": onboarding_request.zip_code,
        "radius_miles": onboarding_request.radius_miles,
        "selected_lat": onboarding_request.selected_lat,
        "selected_lng": onboarding_request.selected_lng,
        "auto_start_queries": False,
        "include_persona_deepening": onboarding_request.include_persona_deepening,
        "include_visit_route": onboarding_request.include_visit_route,
        "include_outreach_preparation": onboarding_request.include_outreach_preparation,
        "max_results": onboarding_request.max_results,
    }
    if spec.flags:
        onboarding_data["simulation_mode"] = spec.flags.simulation_mode
        onboarding_data["regulated_domain"] = spec.flags.regulated_domain
    from src.services.hs_code_service import ensure_hs_code_in_onboarding
    onboarding_data = ensure_hs_code_in_onboarding(onboarding_data)
    plan_data["hs_code"] = onboarding_data.get("hs_code")
    plan_data["hs_code_source"] = onboarding_data.get("hs_code_source")
    plan_data["product_customs_description"] = onboarding_data.get("product_customs_description")

    plans_file = DATA_DIR / "onboarding_plans.jsonl"
    with open(plans_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(plan_data, ensure_ascii=False) + "\n")

    created_by_user_id = None
    try:
        uid = http_request.headers.get("X-User-Id")
        created_by_user_id = int(uid) if uid else None
    except (TypeError, ValueError):
        pass
    try:
        plan_svc = get_plan_service(db)
        plan_svc.create_plan_lifecycle(plan_id, onboarding_data, created_by_user_id=created_by_user_id)
        logger.info(f"Assistant plan lifecycle created: {plan_id}")
    except Exception as e:
        logger.warning(f"Plan lifecycle creation skipped: {str(e)}")

    plan_cache_key = cache_key("plan", plan_id=plan_id)
    set_cache(plan_cache_key, plan_data, ttl=3600)
    return PlanSpecCreatePlanResponse(plan_id=plan_id, created_at=created_at)


@router.get("/assistant/preview-scope/{plan_id}", response_model=PreviewScopeResponse)
async def assistant_preview_scope(
    plan_id: str,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    """
    Preview scope for a plan: estimated_total, sample (capped 100), warnings.
    Use after create-plan, before start-run.
    """
    from src.services.result_service import get_result_service
    try:
        result_service = get_result_service(db)
        preview = result_service.get_preview_report(plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    warnings = []
    if preview.get("warning_message"):
        warnings.append(preview["warning_message"])
    if preview.get("requires_refinement"):
        warnings.append("Region may be large; results capped to 100.")
    return PreviewScopeResponse(
        plan_id=plan_id,
        estimated_total=preview.get("businesses_found", 0),
        sample_100=preview.get("businesses_available_sample", min(100, preview.get("businesses_found", 0))),
        warnings=warnings if warnings else None,
        target_region=preview.get("target_region", ""),
    )


@router.post("/assistant/start-run", response_model=StartRunResponse)
async def assistant_start_run(
    body: StartRunRequest,
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None, alias="Authorization"),
):
    """
    Start run for a plan (orchestrator: plan → run → Results Hub).
    Optionally pass quote_token from pricing/calculate for cost confirmation.
    Admin users (SOARB2B_ADMIN_EMAILS / isanli058@gmail.com) skip quote_token requirement.
    """
    from src.services.query_execution_service import get_query_execution_service
    from src.models.plan_lifecycle import PlanLifecycle

    plan = db.query(PlanLifecycle).filter(PlanLifecycle.plan_id == body.plan_id).first()
    if not plan or not getattr(plan, "onboarding_data", None):
        raise HTTPException(status_code=404, detail=f"Plan {body.plan_id} not found")
    od = plan.onboarding_data if isinstance(plan.onboarding_data, dict) else {}
    target_type = od.get("target_type", "B2B")
    geography = od.get("geography", "")
    decision_roles = od.get("decision_roles", "Decision makers")

    # Admin users skip payment/quote requirement
    admin_email = get_email_from_jwt(authorization)
    is_admin = is_admin_email(admin_email)
    cost_confirmed = is_admin
    if is_admin:
        logger.info("Admin user %s: cost_confirmed=True without quote_token", admin_email)
    if body.quote_token and not is_admin:
        try:
            from src.core.quote_token import validate_quote_token
            validation_result = validate_quote_token(
                quote_token=body.quote_token,
                include_persona_deepening="persona" in (od.get("modules") or []),
                include_visit_route=od.get("include_visit_route", False),
                include_export=True,
                include_outreach_preparation=od.get("include_outreach_preparation", False),
                max_results=min(od.get("max_results", 100), 100),
            )
            cost_confirmed = validation_result.get("valid", False)
        except Exception:
            cost_confirmed = False

    query_service = get_query_execution_service(db)
    result = query_service.start_query_pipeline(
        plan_id=body.plan_id,
        target_type=target_type,
        geography=geography,
        decision_roles=decision_roles,
        auto_approved=True,
        cost_confirmed=cost_confirmed,
    )
    return StartRunResponse(
        success=result.get("success", False),
        plan_id=body.plan_id,
        run_id=result.get("run_id"),
        status=result.get("status", ""),
        message=result.get("message", ""),
        requires_cost_confirmation=result.get("requires_cost_confirmation", False),
        cost_preview=result.get("cost_preview"),
    )


@router.get("/archive")
async def get_archive(
    request: Request,
    plan_ids: Optional[str] = Query(None, description="Comma-separated plan IDs (geçmiş arşiv; tarayıcıda saklanan ID'ler)"),
    limit: int = Query(50, ge=1, le=200),
    api_key: str = Depends(validate_api_key),
    db: Session = Depends(get_db),
):
    """
    Kullanıcı geçmiş arşivi: kendi sorgu/plan kayıtlarını listeler.
    - X-User-Id header: o kullanıcıya ait planlar (created_by_user_id).
    - plan_ids query: verilen plan_id listesi (localStorage ile saklanan ID'ler).
    İkisi de verilmezse boş liste döner.
    """
    from src.models.plan_lifecycle import PlanLifecycle
    query = db.query(PlanLifecycle).order_by(PlanLifecycle.created_at.desc())
    user_id = None
    try:
        uid = request.headers.get("X-User-Id")
        user_id = int(uid) if uid else None
    except (TypeError, ValueError):
        pass
    if user_id is not None:
        query = query.filter(PlanLifecycle.created_by_user_id == user_id)
    if plan_ids:
        ids = [p.strip() for p in plan_ids.split(",") if p.strip()]
        if ids:
            query = query.filter(PlanLifecycle.plan_id.in_(ids))
            if user_id is None:
                pass   # filter only by plan_ids
    if user_id is None and not plan_ids:
        return {"success": True, "count": 0, "plans": []}
    plans = query.limit(limit).all()
    out = []
    for p in plans:
        od = p.onboarding_data or {}
        out.append({
            "plan_id": p.plan_id,
            "geography": od.get("geography"),
            "product_service": od.get("product_service"),
            "hs_code": od.get("hs_code"),
            "current_stage": p.current_stage,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    return {"success": True, "count": len(out), "plans": out}


@router.get("/case-library/cases")
async def get_case_library(
    access_level: str = Query("public", description="Filter by access level"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    region: Optional[str] = Query(None, description="Filter by region"),
    api_key: str = Depends(validate_api_key)
):
    """Get case library entries filtered by access level, sector, and region"""
    if access_level not in ["public", "sales", "internal"]:
        raise HTTPException(
            status_code=400,
            detail="access_level must be one of: public, sales, internal"
        )
    
    all_cases = _get_all_cases()
    filtered_cases = []
    
    for case_data in all_cases:
        # Access level filtering
        case_access = case_data.get("meta", {}).get("access_level") or case_data.get("access_level")
        if case_access != access_level and access_level != "internal":
            continue
        
        # Sector filtering
        if sector:
            case_sector = case_data.get("meta", {}).get("sector") or case_data.get("metadata", {}).get("sector")
            if case_sector != sector:
                continue
        
        # Region filtering
        if region:
            case_region = case_data.get("meta", {}).get("region") or case_data.get("metadata", {}).get("region")
            if case_region != region:
                continue
        
        filtered_cases.append(case_data)
    
    return {"cases": filtered_cases}


@router.get("/case-library/cases/{case_id}")
async def get_case_by_id(
    case_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get a specific case by ID"""
    if not CASE_LIBRARY_DIR.exists():
        raise HTTPException(status_code=404, detail="Case library not found")
    
    # Try exact filename match first
    case_file = CASE_LIBRARY_DIR / f"{case_id}.json"
    
    # If not found, search all files for matching case_id
    if not case_file.exists():
        all_cases = _get_all_cases()
        for case_data in all_cases:
            meta_case_id = case_data.get("meta", {}).get("case_id")
            legacy_case_id = case_data.get("case_id")
            if meta_case_id == case_id or legacy_case_id == case_id:
                return case_data
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found")
    
    case_data = _load_case_file(case_file)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found or could not be loaded")
    
    return case_data


@router.get("/case-library/cases/{case_id}/analysis")
async def get_case_analysis(
    case_id: str,
    api_key: str = Depends(validate_api_key)
):
    """Get analysis result for a specific case (analysis_result + case_id + access_level only)"""
    if not CASE_LIBRARY_DIR.exists():
        raise HTTPException(status_code=404, detail="Case library not found")
    
    # Try exact filename match first
    case_file = CASE_LIBRARY_DIR / f"{case_id}.json"
    case_data = None
    
    if case_file.exists():
        case_data = _load_case_file(case_file)
    else:
        # Search all files for matching case_id
        all_cases = _get_all_cases()
        for c in all_cases:
            meta_case_id = c.get("meta", {}).get("case_id")
            legacy_case_id = c.get("case_id")
            if meta_case_id == case_id or legacy_case_id == case_id:
                case_data = c
                break
    
    if not case_data:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found")
    
    # Extract required fields
    meta = case_data.get("meta", {})
    access_level = meta.get("access_level") or case_data.get("access_level")
    analysis_result = case_data.get("analysis_result")
    
    if not analysis_result:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis result not found for case '{case_id}'"
        )
    
    return {
        "case_id": meta.get("case_id") or case_data.get("case_id"),
        "access_level": access_level,
        "analysis_result": analysis_result
    }


@router.get("/demo/hotels")
async def get_demo_hotels(
    location: Optional[str] = Query(None, description="Location query (city, zip code, address)"),
    zip_code: Optional[str] = Query(None, description="Zip code (e.g., 75230)"),
    latitude: Optional[float] = Query(None, description="Latitude coordinate"),
    longitude: Optional[float] = Query(None, description="Longitude coordinate"),
    api_key: str = Depends(validate_api_key)
):
    """
    Get verified hotel targets for showcase.
    Returns real hotel data from verified sources (Google Places API or case library).
    Supports location-based search via location query, zip code, or coordinates.
    Cached for 5 minutes per location.
    """
    # Generate cache key
    cache_key_str = cache_key("hotels", location=location, zip_code=zip_code, lat=latitude, lng=longitude)
    
    # Try cache first
    cached_result = get_cache(cache_key_str)
    if cached_result is not None:
        logger.debug(f"Cache hit: hotels:{cache_key_str}")
        from fastapi.responses import JSONResponse
        response = JSONResponse(content=cached_result)
        response.headers["X-Cache"] = "HIT"
        return response
    
    logger.debug(f"Cache miss: hotels:{cache_key_str}")
    
    # Try to get real data from Google Places API if available
    google_places_key = os.getenv("GOOGLE_PLACES_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
    
    hotels = []
    search_location = None
    search_coords = None
    
    # Determine search location
    if zip_code:
        # Use zip code as search query
        search_location = zip_code
    elif location:
        # Use provided location
        search_location = location
    elif latitude and longitude:
        # Use coordinates
        search_coords = (latitude, longitude)
        search_location = f"{latitude},{longitude}"
    
    if google_places_key:
        # Use Google Places API for real hotel data
        try:
            # If coordinates provided, use nearby search; otherwise use text search
            if search_coords:
                # Use Nearby Search API for coordinates
                url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                params = {
                    "location": f"{latitude},{longitude}",
                    "radius": "5000",   # 5km radius
                    "type": "lodging",
                    "key": google_places_key
                }
            else:
                # Use Text Search API for location/zip code
                if not search_location:
                    # Default fallback (should not happen if location provided)
                    search_location = "Dallas, TX"
                
                url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                query_text = f"hotel {search_location}"
                params = {
                    "query": query_text,
                    "key": google_places_key,
                    "type": "lodging"
                }
            
            target_roles = ["Procurement Manager", "Housekeeping Manager", "Operations Manager"]
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])[:12]   # Max 12 hotels
                    
                    for idx, place in enumerate(results):
                        hotel_name = place.get("name", "")
                        formatted_address = place.get("formatted_address", "")
                        
                        # Extract location info from address
                        address_parts = formatted_address.split(",")
                        location_str = address_parts[0].strip() if address_parts else search_location
                        
                        # Get coordinates if available
                        geometry = place.get("geometry", {})
                        location_coords = geometry.get("location", {})
                        
                        # Assign roles based on hotel index (for variety)
                        role_combos = [
                            ["Procurement Manager", "Housekeeping Manager"],
                            ["Procurement Manager", "Operations Manager"],
                            ["Housekeeping Manager", "Procurement Manager"],
                            ["Operations Manager", "Procurement Manager", "Housekeeping Manager"]
                        ]
                        roles = role_combos[idx % len(role_combos)]
                        
                        hotel_data = {
                            "id": f"hotel-{len(hotels) + 1}",
                            "name": hotel_name,
                            "location": location_str,
                            "roles": roles,
                            "verified": True
                        }
                        
                        # Add coordinates if available
                        if location_coords:
                            hotel_data["latitude"] = location_coords.get("lat")
                            hotel_data["longitude"] = location_coords.get("lng")
                        
                        hotels.append(hotel_data)
            except Exception as e:
                # If API fails, continue with fallback data
                logger.error(f"Google Places API error: {e}")
                pass
                
        except Exception as e:
            # Fallback to curated real hotel data if API fails
            pass
    
    # Fallback: Use curated list only if no location specified and API failed
    # If location was specified, return empty list rather than wrong location data
    if not hotels and not search_location and not search_coords:
        hotels = [
            {
                "id": "hotel-1",
                "name": "The Marmara Taksim",
                "location": "Istanbul, Taksim Square",
                "roles": ["Procurement Manager", "Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-2",
                "name": "Mardan Palace",
                "location": "Antalya, Lara Beach",
                "roles": ["Procurement Manager", "Operations Manager"],
                "verified": True
            },
            {
                "id": "hotel-3",
                "name": "Swissotel The Bosphorus",
                "location": "Istanbul, Beşiktaş",
                "roles": ["Housekeeping Manager", "Procurement Manager"],
                "verified": True
            },
            {
                "id": "hotel-4",
                "name": "Hilton Istanbul Bomonti",
                "location": "Istanbul, Şişli",
                "roles": ["Procurement Manager", "Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-5",
                "name": "Rixos Downtown Antalya",
                "location": "Antalya, Konyaaltı",
                "roles": ["Operations Manager", "Procurement Manager"],
                "verified": True
            },
            {
                "id": "hotel-6",
                "name": "Four Seasons Hotel Istanbul at Sultanahmet",
                "location": "Istanbul, Sultanahmet",
                "roles": ["Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-7",
                "name": "Divan Ankara",
                "location": "Ankara, Çankaya",
                "roles": ["Procurement Manager", "Operations Manager", "Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-8",
                "name": "Concorde De Luxe Resort",
                "location": "Antalya, Side",
                "roles": ["Procurement Manager", "Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-9",
                "name": "W Istanbul",
                "location": "Istanbul, Beşiktaş",
                "roles": ["Procurement Manager"],
                "verified": True
            },
            {
                "id": "hotel-10",
                "name": "Ankara HiltonSA",
                "location": "Ankara, Kavaklıdere",
                "roles": ["Housekeeping Manager", "Operations Manager"],
                "verified": True
            },
            {
                "id": "hotel-11",
                "name": "Çırağan Palace Kempinski",
                "location": "Istanbul, Beşiktaş",
                "roles": ["Procurement Manager", "Housekeeping Manager"],
                "verified": True
            },
            {
                "id": "hotel-12",
                "name": "Rixos Sungate",
                "location": "Antalya, Kemer",
                "roles": ["Operations Manager", "Procurement Manager"],
                "verified": True
            }
        ]
    
    result = {"hotels": hotels}
    
    # Cache result (TTL: 5 minutes = 300 seconds)
    set_cache(cache_key_str, result, ttl=300)
    
    # Add cache header (MISS because we just cached it)
    from fastapi.responses import JSONResponse
    response = JSONResponse(content=result)
    response.headers["X-Cache"] = "MISS"
    return response
