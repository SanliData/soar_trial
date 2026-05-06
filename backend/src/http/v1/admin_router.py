"""
ROUTER: admin_router
PURPOSE: Admin intervention endpoints for plan management
ENCODING: UTF-8 WITHOUT BOM

ADMIN ONLY - Requires separate admin API key validation.
Admins: users list, support messages + reply, contact intakes, plan approve/suggest/edit.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.db.base import get_db, IS_SQLITE, IS_POSTGRESQL
from src.services.plan_service import get_plan_service
from src.services.auth_service import get_auth_service, get_admin_emails
from src.core.query_limits import ADMIN_MAX_RESULTS_OVERRIDE, MAX_RESULTS_PER_QUERY
from src.models.plan_lifecycle import PlanLifecycle
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Data directory (support_messages, onboarding_intakes, admin_replies)
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def _admin_emails() -> List[str]:
    """List of emails allowed as admin (SOARB2B_ADMIN_EMAILS)."""
    return get_admin_emails()


# Admin validation: X-Admin-Key OR JWT for allowed admin email
def validate_admin_key(
    admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    authorization: Optional[str] = Header(None),
) -> str:
    """Validate admin: X-Admin-Key (SOARB2B_ADMIN_KEYS) or Bearer JWT for SOARB2B_ADMIN_EMAILS."""
    # 1) Try API key
    if admin_key and admin_key.strip():
        key = admin_key.strip()
        allowed_keys_env = os.getenv("SOARB2B_ADMIN_KEYS", "")
        allowed_keys = [k.strip() for k in allowed_keys_env.split(",") if k.strip()]
        if not allowed_keys and os.getenv("ENV") == "production":
            raise HTTPException(status_code=500, detail="Admin keys are not configured")
        if key in allowed_keys:
            return key

    # 2) Try Bearer JWT and admin-email list
    admin_emails = _admin_emails()
    if authorization and authorization.strip().lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token and admin_emails:
            auth_service = get_auth_service()
            result = auth_service.verify_jwt_token(token)
            if result.get("success") and result.get("payload"):
                email = (result.get("payload") or {}).get("email")
                if email and isinstance(email, str) and email.strip().lower() in admin_emails:
                    return f"admin:{email.strip().lower()}"

    if admin_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    raise HTTPException(status_code=401, detail="X-Admin-Key or Bearer token (admin email) required")


# Request Models
class AdminInterventionRequest(BaseModel):
    """Admin intervention parameters"""
    # Persona scope adjustments
    persona_scope_adjustment: Optional[str] = Field(None, description="Expand or restrict persona scope")
    role_strictness: Optional[str] = Field(None, description="Strict, moderate, or flexible role matching")
    
    # Channel priority
    channel_priority: Optional[Dict[str, int]] = Field(None, description="Channel priority order (email=1, linkedin=2, etc.)")
    
    # Exposure radius
    exposure_radius_km: Optional[float] = Field(None, description="Exposure radius in kilometers")
    
    # Compliance flags
    compliance_flags: Optional[Dict[str, Any]] = Field(None, description="Compliance flags (GDPR, CCPA, etc.)")
    
    # Partner selection
    partner_id: Optional[str] = Field(None, description="Partner ID for managed exposure")
    
    # Admin note (visible to user as "Custom strategy applied")
    admin_note: Optional[str] = Field(None, description="Note visible to user (e.g., 'Custom strategy applied')")
    
    # Stage advancement (admin can manually advance stages)
    advance_stage: Optional[str] = Field(None, description="Advance to stage (ANALYSIS_READY, PERSONA_REVIEW, etc.)")
    # Firmaya özel sorgu algoritması (company-specific query algorithm)
    company_algorithm_params: Optional[Dict[str, Any]] = Field(None, description="Company-specific algorithm params (JSON)")


class AdminInterventionResponse(BaseModel):
    """Admin intervention response"""
    success: bool
    plan_id: str
    interventions_applied: Dict[str, Any]
    admin_note: Optional[str] = None
    updated_at: str


class AdminActionRequest(BaseModel):
    """Strategist quick action: note, mode, add-ons, approve or save draft."""
    admin_note: Optional[str] = Field(None, description="Admin note (visible to user as guidance)")
    algorithm_mode: Optional[str] = Field("standard", description="standard | customized")
    recommended_addons: Optional[List[str]] = Field(None, description="e.g. visit_route, partner_ads")
    action: Optional[str] = Field(None, description="approve | save_draft")


# Endpoints
@router.post("/plan/{plan_id}/intervene", response_model=AdminInterventionResponse)
async def admin_intervene(
    plan_id: str,
    intervention: AdminInterventionRequest,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db)
):
    """
    Admin intervention: adjust scope, priority, apply custom strategy.
    All changes are marked as "Custom strategy applied" on user side.
    """
    try:
        plan_service = get_plan_service(db)
        plan = plan_service.get_plan(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        
        interventions_applied = {}
        
        # Apply persona scope adjustment
        if intervention.persona_scope_adjustment:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["persona_scope"] = intervention.persona_scope_adjustment
            interventions_applied["persona_scope"] = intervention.persona_scope_adjustment
        
        # Apply role strictness
        if intervention.role_strictness:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["role_strictness"] = intervention.role_strictness
            interventions_applied["role_strictness"] = intervention.role_strictness
        
        # Apply channel priority
        if intervention.channel_priority:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["channel_priority"] = intervention.channel_priority
            interventions_applied["channel_priority"] = intervention.channel_priority
        
        # Apply exposure radius
        if intervention.exposure_radius_km is not None:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["exposure_radius_km"] = intervention.exposure_radius_km
            interventions_applied["exposure_radius_km"] = intervention.exposure_radius_km
        
        # Apply compliance flags
        if intervention.compliance_flags:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["compliance_flags"] = intervention.compliance_flags
            interventions_applied["compliance_flags"] = intervention.compliance_flags
        
        # Apply partner selection
        if intervention.partner_id:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["partner_id"] = intervention.partner_id
            interventions_applied["partner_id"] = intervention.partner_id
        
        # Add admin note (visible to user)
        if intervention.admin_note:
            plan.admin_note = intervention.admin_note
        
        # Firmaya özel sorgu algoritması
        if intervention.company_algorithm_params is not None:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["company_algorithm_params"] = intervention.company_algorithm_params
            interventions_applied["company_algorithm_params"] = intervention.company_algorithm_params
        
        # Mark as intervened
        plan.admin_intervened = True
        
        # Advance stage if requested
        if intervention.advance_stage:
            plan.current_stage = intervention.advance_stage
            if intervention.advance_stage == "ANALYSIS_READY" and not plan.analysis_ready_at:
                plan.analysis_ready_at = datetime.utcnow()
            elif intervention.advance_stage == "PERSONA_REVIEW" and not plan.persona_review_at:
                plan.persona_review_at = datetime.utcnow()
            interventions_applied["stage_advanced"] = intervention.advance_stage
        
        db.commit()
        db.refresh(plan)
        
        return AdminInterventionResponse(
            success=True,
            plan_id=plan_id,
            interventions_applied=interventions_applied,
            admin_note=plan.admin_note or "Custom strategy applied",
            updated_at=plan.updated_at.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying admin intervention: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to apply admin intervention")


@router.get("/plan/{plan_id}")
async def get_plan_details(
    plan_id: str,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db)
):
    """
    Admin view: Get full plan details including:
    - Original user input (read-only)
    - System interpretation
    - Admin adjustments
    - Current status
    """
    try:
        plan_service = get_plan_service(db)
        plan = plan_service.get_plan(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        
        # Get all objectives
        objectives = [
            {
                "type": obj.objective_type,
                "status": obj.status,
                "selected_at": obj.selected_at.isoformat(),
                "approved_at": obj.approved_at.isoformat() if obj.approved_at else None,
                "activated_at": obj.activated_at.isoformat() if obj.activated_at else None
            }
            for obj in plan.objectives
        ]
        
        # Get all stages
        stages = [
            {
                "name": stage.stage_name,
                "order": stage.stage_order,
                "status": stage.status,
                "started_at": stage.started_at.isoformat() if stage.started_at else None,
                "completed_at": stage.completed_at.isoformat() if stage.completed_at else None,
                "admin_note": stage.admin_note
            }
            for stage in plan.stages
        ]
        
        od = plan.onboarding_data or {}
        return {
            "plan_id": plan.plan_id,
            "onboarding_data": od,
            "selected_objectives": plan.selected_objectives or od.get("selected_objectives"),
            "current_stage": plan.current_stage,
            "status": plan.status,
            "admin_intervened": plan.admin_intervened,
            "admin_adjustments": plan.admin_adjustments or {},
            "admin_note": plan.admin_note,
            "objectives": objectives,
            "stages": stages,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan details: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get plan details")


@router.get("/plan/{plan_id}/results")
async def get_plan_results_admin(
    plan_id: str,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db)
):
    """
    Admin view: Results Hub for a plan (modules, status, preview).
    Same data as user-facing GET /api/v1/b2b/plans/{plan_id}/results but with admin auth.
    """
    try:
        from src.services.result_service import get_result_service
        result_service = get_result_service(db)
        data = result_service.get_results(plan_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting plan results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get plan results")


@router.post("/plan/{plan_id}/admin-action")
async def admin_plan_action(
    plan_id: str,
    body: AdminActionRequest,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db),
):
    """
    Strategist quick action: save admin note, set mode, recommend add-ons, approve or save as draft.
    """
    try:
        plan_service = get_plan_service(db)
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        if body.admin_note is not None:
            plan.admin_note = body.admin_note.strip() or None
        if body.algorithm_mode:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["algorithm_mode"] = body.algorithm_mode
        if body.recommended_addons is not None:
            if not plan.admin_adjustments:
                plan.admin_adjustments = {}
            plan.admin_adjustments["recommended_addons"] = body.recommended_addons
        plan.admin_intervened = True
        if body.action == "approve":
            plan.current_stage = "QUERY_EXECUTING"
            plan.status = "active"
        elif body.action == "save_draft":
            plan.status = "paused"
        db.commit()
        db.refresh(plan)
        return {
            "success": True,
            "plan_id": plan_id,
            "admin_note": plan.admin_note,
            "action": body.action,
            "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in admin plan action: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to apply admin action")


@router.post("/query-cap-override")
async def override_query_cap(
    override_request: Dict[str, Any],
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db)
):
    """
    Admin-only: Override query cap for specific plan.
    Default user cap: 100 results per query.
    Admin cap override: up to 1000 results (still capped for safety).
    """
    try:
        plan_id = override_request.get("plan_id")
        new_cap = override_request.get("new_cap", ADMIN_MAX_RESULTS_OVERRIDE)
        
        # Enforce admin override limit
        new_cap = min(new_cap, ADMIN_MAX_RESULTS_OVERRIDE)
        new_cap = max(new_cap, MAX_RESULTS_PER_QUERY)   # Cannot go below default
        
        # TODO: Store override in plan or admin config
        # For now, return the override limit
        
        return {
            "success": True,
            "plan_id": plan_id,
            "original_cap": MAX_RESULTS_PER_QUERY,
            "override_cap": new_cap,
            "note": f"Admin override applied. Query cap set to {new_cap} results (admin limit: {ADMIN_MAX_RESULTS_OVERRIDE})"
        }
    except Exception as e:
        logger.error(f"Error overriding query cap: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to override query cap")


def _plan_status_badge(current_stage: str, status: str) -> str:
    """Human-friendly status for strategist dashboard."""
    if status == "completed":
        return "Completed"
    if status == "cancelled":
        return "Cancelled"
    if current_stage in ("QUERY_EXECUTING", "EXPOSURE_RUNNING"):
        return "Auto-Running"
    if current_stage in ("CREATED", "ANALYSIS_READY", "PERSONA_REVIEW"):
        return "Pending Review"
    if current_stage in ("EXPOSURE_READY", "SOFT_CONVERSION", "DIRECT_OUTREACH"):
        return "In Progress"
    return "Pending Review"


# --- Admin: Plan list (strategist queue: short_id, product, region, goal, status badge) ---
@router.get("/plans")
async def admin_list_plans(
    limit: int = 100,
    status_filter: Optional[str] = None,
    region_filter: Optional[str] = None,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db),
):
    """
    Admin-only: List plans for strategist dashboard.
    Returns short_plan_id, product, region, objective, meeting_goal, status_badge, created_at.
    """
    try:
        query = db.query(PlanLifecycle).order_by(PlanLifecycle.created_at.desc())
        if status_filter:
            if status_filter == "pending_review":
                query = query.filter(
                    PlanLifecycle.current_stage.in_(["CREATED", "ANALYSIS_READY", "PERSONA_REVIEW"]),
                    PlanLifecycle.status == "active",
                )
            elif status_filter == "active":
                query = query.filter(PlanLifecycle.status == "active")
            elif status_filter == "completed":
                query = query.filter(PlanLifecycle.status == "completed")
        plans = query.limit(limit).all()
        od_list = []
        for p in plans:
            od = p.onboarding_data or {}
            geography = od.get("geography") or od.get("region") or ""
            if region_filter and geography and region_filter.lower() not in (geography or "").lower():
                continue
            short_id = (p.plan_id or "")[-8:] if len(p.plan_id or "") >= 8 else (p.plan_id or "")
            od_list.append({
                "plan_id": p.plan_id,
                "short_plan_id": short_id,
                "current_stage": p.current_stage,
                "status": p.status,
                "status_badge": _plan_status_badge(p.current_stage, p.status or ""),
                "admin_intervened": p.admin_intervened,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "geography": geography,
                "product_service": od.get("product_service") or od.get("target_type") or "",
                "target_type": od.get("target_type") or "",
                "meeting_goal": od.get("meeting_goal") or od.get("monthly_meetings") or "",
                "decision_roles": od.get("decision_roles") or "",
                "hs_code": od.get("hs_code"),
            })
        return {
            "success": True,
            "count": len(od_list),
            "plans": od_list,
        }
    except Exception as e:
        logger.error("Error listing plans: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list plans")


# --- Admin: Upload visibility (who uploaded what, abuse suspicion) ---
@router.get("/uploads")
async def admin_list_uploads(
    limit: int = 100,
    upload_type: Optional[str] = None,
    abuse_only: bool = False,
    admin_key: str = Depends(validate_admin_key),
):
    """
    Admin-only: List recent uploads (LinkedIn profile, company target).
    Shows: who (IP), what (type, payload), preview, abuse_suspicion.
    """
    try:
        from src.services.upload_service import list_uploads
        records = list_uploads(limit=limit, upload_type=upload_type, abuse_only=abuse_only)
        return {
            "success": True,
            "count": len(records),
            "uploads": records,
        }
    except Exception as e:
        logger.error(f"Error listing uploads: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list uploads")


def _read_jsonl(path: Path, limit: int = 200) -> List[Dict[str, Any]]:
    """Read JSONL file and return list of records (newest first)."""
    if not path.exists():
        return []
    records = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logger.warning("Read JSONL %s: %s", path, e)
    records.reverse()
    return records[:limit]


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# --- Admin: Tüm kullanıcı hesapları (gerçek veritabanı: users tablosu) ---
@router.get("/users")
async def admin_list_users(
    limit: int = 200,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db),
):
    """Admin: Tüm kullanıcı hesaplarını listele. Veri kaynağı: veritabanı (users tablosu)."""
    try:
        # Gerçek tablo sayısı (doğrulama için)
        total_in_db = db.query(User).count()
        users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
        db_type = "postgresql" if IS_POSTGRESQL else ("sqlite" if IS_SQLITE else "database")
        return {
            "success": True,
            "count": len(users),
            "total_in_db": total_in_db,
            "source": "database",
            "table": "users",
            "database_type": db_type,
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
                for u in users
            ],
        }
    except Exception as e:
        logger.error("Error listing users: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list users")


# --- Admin: Mesaj kutusu (iletişim formundan gelen mesajlar + yanıt) ---
@router.get("/support-messages")
async def admin_list_support_messages(
    limit: int = 100,
    admin_key: str = Depends(validate_admin_key),
):
    """Admin: İletişim formundan gelen mesajları listele."""
    path = DATA_DIR / "support_messages.jsonl"
    records = _read_jsonl(path, limit=limit)
    replies_path = DATA_DIR / "admin_replies.jsonl"
    replies_by_msg = {}
    if replies_path.exists():
        for r in _read_jsonl(replies_path, limit=1000):
            mid = r.get("message_id")
            if mid:
                replies_by_msg.setdefault(mid, []).append(r)
    for r in records:
        r["replies"] = replies_by_msg.get(r.get("message_id"), [])
    return {"success": True, "count": len(records), "messages": records}


class ReplyRequest(BaseModel):
    reply_text: str = Field(..., description="Yanıt metni")


@router.post("/support-messages/{message_id}/reply")
async def admin_reply_to_message(
    message_id: str,
    body: ReplyRequest,
    admin_key: str = Depends(validate_admin_key),
):
    """Admin: Mesaja yanıt kaydet (kullanıcıya e-posta gönderimi ayrı entegrasyon)."""
    path = DATA_DIR / "admin_replies.jsonl"
    record = {
        "message_id": message_id,
        "reply_text": body.reply_text,
        "replied_at": datetime.utcnow().isoformat(),
        "admin": "admin",
    }
    _append_jsonl(path, record)
    return {"success": True, "message_id": message_id, "replied_at": record["replied_at"]}


# --- Admin: İletişim kutusundan gelen talepler (onboarding intakes) ---
@router.get("/contact-intakes")
async def admin_list_contact_intakes(
    limit: int = 100,
    admin_key: str = Depends(validate_admin_key),
):
    """Admin: İletişim / onboarding taleplerini listele."""
    path = DATA_DIR / "onboarding_intakes.jsonl"
    records = _read_jsonl(path, limit=limit)
    return {"success": True, "count": len(records), "intakes": records}


# --- Admin: Sorgu talebini onayla (onaylarsa sorgu direkt başlasın) ---
@router.post("/plan/{plan_id}/approve")
async def admin_approve_plan(
    plan_id: str,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db),
):
    """Admin: Sorgu talebini onayla; plan ANALYSIS_READY yapıp sorguyu başlatır."""
    try:
        plan_service = get_plan_service(db)
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        plan.current_stage = "ANALYSIS_READY"
        plan.analysis_ready_at = plan.analysis_ready_at or datetime.utcnow()
        plan.admin_intervened = True
        plan.admin_note = (plan.admin_note or "").strip() or "Sorgu onaylandı, işlem başlatıldı."
        from src.models.plan_lifecycle import PlanStage
        market_scan = db.query(PlanStage).filter(
            PlanStage.plan_id == plan_id,
            PlanStage.stage_name == "market_scan",
        ).first()
        if market_scan:
            market_scan.status = "in_progress"
            market_scan.started_at = market_scan.started_at or datetime.utcnow()
        db.commit()
        return {
            "success": True,
            "plan_id": plan_id,
            "message": "Sorgu onaylandı, işlem başlatıldı.",
            "current_stage": plan.current_stage,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error approving plan: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to approve plan")


# --- Admin: Replay endpoint (Acontext observability) ---
@router.get("/replay/{trace_id}")
async def admin_replay(
    trace_id: str,
    tenant_id: Optional[str] = Query(None, description="Tenant ID for isolation (required for cross-tenant check)"),
    admin_key: str = Depends(validate_admin_key),
):
    """
    Admin-only: Get full ordered event timeline for replay.
    Returns gate decisions, tool calls, artifacts for the given trace_id.
    Tenant isolation: if tenant_id provided, only events for that tenant are returned.
    """
    try:
        from src.integrations.acontext_client import get_events_for_replay
        from src.security.context_guard import extract_tenant_from_context

        request_tenant_id = tenant_id or extract_tenant_from_context()
        events = await get_events_for_replay(trace_id=trace_id, tenant_id=request_tenant_id)

        # Build ordered timeline
        timeline = []
        gate_decisions = []
        tool_calls = []
        artifacts = []

        for ev in events:
            ev_type = ev.get("type")
            payload = ev.get("payload", {})
            entry = {"type": ev_type, "payload": payload, "ts": payload.get("ts")}
            timeline.append(entry)
            if ev_type == "EVENT":
                p = payload.get("payload", payload)
                if isinstance(p, dict):
                    if p.get("event_type") == "UPAP_GATE_RESULT" or "gate_name" in p:
                        gate_decisions.append(entry)
                    elif p.get("event_type") == "TOOL_CALL" or "tool_name" in p:
                        tool_calls.append(entry)
                    elif p.get("event_type") == "AGENT_METRIC":
                        pass   # included in timeline
            elif ev_type == "ARTIFACT":
                artifacts.append(entry)

        return {
            "success": True,
            "trace_id": trace_id,
            "tenant_id": request_tenant_id,
            "timeline": timeline,
            "gate_decisions": gate_decisions,
            "tool_calls": tool_calls,
            "artifacts": artifacts,
            "count": len(timeline),
        }
    except Exception as e:
        logger.error("Replay failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Replay failed: {str(e)}")


# --- Admin: Sorgu talebi için öneri (kullanıcıya erişir - admin_note) ---
class SuggestRequest(BaseModel):
    suggestion: str = Field(..., description="Kullanıcıya gösterilecek öneri metni")


@router.post("/plan/{plan_id}/suggest")
async def admin_suggest_plan(
    plan_id: str,
    body: SuggestRequest,
    admin_key: str = Depends(validate_admin_key),
    db: Session = Depends(get_db),
):
    """Admin: Sorgu talebi için öneri ekle (kullanıcı timeline/plan detayında görür)."""
    try:
        plan_service = get_plan_service(db)
        plan = plan_service.get_plan(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        plan.admin_note = body.suggestion
        plan.admin_intervened = True
        db.commit()
        return {
            "success": True,
            "plan_id": plan_id,
            "message": "Öneri kaydedildi, kullanıcıya görünecek.",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error suggesting plan: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save suggestion")
